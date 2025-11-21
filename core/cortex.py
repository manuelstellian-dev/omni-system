from pydantic import BaseModel, Field
from typing import List
import litellm
import json
import os
from resource_monitor import ResourceMonitor


class Task(BaseModel):
    """
    Represents a single task in the execution plan DAG.
    """
    task_id: str = Field(..., description="Unique identifier for the task (e.g., 'setup_database', 'create_auth_api')")
    task_description: str = Field(..., description="Detailed description of what this task accomplishes")
    output_files: List[str] = Field(..., description="List of files this task will generate (e.g., ['prisma/schema.prisma', 'src/lib/db.ts'])")
    depends_on: List[str] = Field(default_factory=list, description="List of task_ids that must complete before this task (for DAG ordering)")


class ProjectSpec(BaseModel):
    """
    Complete project specification including execution plan DAG.
    """
    project_name: str = Field(..., description="The name of the project")
    tech_stack: List[str] = Field(..., description="List of technologies to be used")
    database_schema: str = Field(..., description="Text description of the database schema")
    core_features: List[str] = Field(..., description="List of core features to implement")
    execution_plan: List[Task] = Field(..., description="Ordered task execution plan as a DAG (Directed Acyclic Graph)")


def analyze_intent(intent: str) -> ProjectSpec:
    """
    Analyzes user intent and returns a structured ProjectSpec with execution plan DAG.
    Uses LiteLLM to connect to any model (assumes env vars are set).
    """
    system_prompt = """You are OMNI's Cortex - an expert software architect and task planner.
Your role is to analyze user intent and produce a STRICT JSON specification with a complete execution plan.

Given a user's project description, you must output ONLY valid JSON matching this schema:
{
  "project_name": "string - kebab-case project name",
  "tech_stack": ["array", "of", "technologies"],
  "database_schema": "detailed text description of tables, fields, and relationships",
  "core_features": ["array", "of", "core", "features"],
  "execution_plan": [
    {
      "task_id": "unique_task_identifier",
      "task_description": "detailed description of what this task accomplishes",
      "output_files": ["list", "of", "file", "paths", "this", "task", "generates"],
      "depends_on": ["list", "of", "task_ids", "that", "must", "complete", "first"]
    }
  ]
}

CRITICAL RULES FOR EXECUTION PLAN:
1. **THE EXECUTION PLAN MUST BE A VALID DAG (Directed Acyclic Graph).**
   - No circular dependencies allowed.
   - Each task_id must be unique.
   - All task_ids in "depends_on" must reference existing tasks defined earlier in the plan.

2. **DEPENDENCIES MUST BE LOGICAL:**
   - Database schema tasks have NO dependencies (they come first).
   - API endpoints DEPEND ON database schema tasks.
   - Frontend components DEPEND ON API endpoints (if they consume them).
   - Authentication DEPENDS ON database schema.
   - Webhooks/Integrations DEPEND ON database schema and authentication.
   - Infrastructure (Docker, CI/CD) has NO dependencies on code (can run in parallel).

3. **TASK GRANULARITY:**
   - Break the project into 5-15 meaningful tasks.
   - Each task should generate 1-5 related files.
   - Tasks should be atomic and independently verifiable.

4. **OUTPUT FILES:**
   - Must be specific file paths (e.g., "src/app/api/auth/route.ts", not "auth files").
   - Include all critical files: schemas, APIs, components, configs, tests.

5. **GENERAL:**
   - Output ONLY valid JSON, no markdown, no explanations.
   - Be opinionated - choose modern, production-grade tech.
   - Database schema must be detailed (include field types, relationships).
   - Features must be specific and actionable.

EXAMPLE EXECUTION PLAN STRUCTURE:
[
  {
    "task_id": "setup_database_schema",
    "task_description": "Define Prisma database schema with User, Appointment, and Booking models",
    "output_files": ["prisma/schema.prisma", "src/lib/db.ts"],
    "depends_on": []
  },
  {
    "task_id": "create_auth_system",
    "task_description": "Implement NextAuth authentication with email/password and OAuth providers",
    "output_files": ["src/app/api/auth/[...nextauth]/route.ts", "src/lib/auth.ts"],
    "depends_on": ["setup_database_schema"]
  },
  {
    "task_id": "create_booking_api",
    "task_description": "Create RESTful API endpoints for appointment booking with validation",
    "output_files": ["src/app/api/bookings/route.ts", "src/app/api/bookings/[id]/route.ts"],
    "depends_on": ["setup_database_schema", "create_auth_system"]
  }
]
"""

    user_prompt = f"Project Intent: {intent}\n\nOutput the complete JSON specification with execution plan DAG:"

    response = litellm.completion(
        model=os.getenv("OMNI_MODEL", "gpt-4o"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    response_text = response.choices[0].message.content
    spec_data = json.loads(response_text)

    return ProjectSpec(**spec_data)
