import * as React from 'react';
import {
  Html,
  Head,
  Body,
  Container,
  Text,
  Button,
  Section,
  Hr,
  Img,
  Tailwind,
} from '@react-email/components';

interface WelcomeEmailProps {
  userName: string;
  signInLink: string;
  appName?: string;
}

const baseUrl = process.env.NEXT_PUBLIC_APP_URL
  ? `https://${process.env.NEXT_PUBLIC_APP_URL}`
  : 'http://localhost:3000'; // Fallback for local development

export const WelcomeEmail = ({
  userName = 'Valued User',
  signInLink = `${baseUrl}/auth/signin`,
  appName = 'saas-boilerplate',
}: WelcomeEmailProps) => (
  <Html>
    <Head />
    <Tailwind>
      <Body className="bg-gray-100 font-sans">
        <Container className="mx-auto my-10 rounded border border-solid border-gray-200 bg-white p-8 shadow-lg">
          <Section className="text-center">
            {/* Optional: Add a logo here */}
            {/* <Img
              src={`${baseUrl}/static/logo.png`} // Replace with your actual logo path
              width="100"
              height="100"
              alt={appName}
              className="mx-auto my-5"
            /> */}
            <Text className="text-2xl font-bold text-gray-800">Welcome to {appName}!</Text>
          </Section>
          <Hr className="my-6 border-t border-solid border-gray-300" />
          <Text className="text-base text-gray-700">Hi {userName},</Text>
          <Text className="text-base text-gray-700">
            Thank you for joining {appName}! We're excited to have you on board.
          </Text>
          <Text className="text-base text-gray-700">
            To get started, please click the button below to sign in to your account.
          </Text>
          <Section className="my-8 text-center">
            <Button
              className="rounded-md bg-blue-600 px-6 py-3 text-base font-semibold text-white no-underline"
              href={signInLink}
            >
              Sign In to Your Account
            </Button>
          </Section>
          <Text className="text-base text-gray-700">
            If you have any questions, feel free to reply to this email.
          </Text>
          <Text className="text-base text-gray-700">
            Best regards,
            <br />
            The {appName} Team
          </Text>
          <Hr className="my-6 border-t border-solid border-gray-300" />
          <Text className="text-center text-xs text-gray-500">
            &copy; {new Date().getFullYear()} {appName}. All rights reserved.
          </Text>
        </Container>
      </Body>
    </Tailwind>
  </Html>
);

export default WelcomeEmail;
