# Enhanced VPC AWS CDK Construct

The `EnhancedVPC` construct provides a flexible and easy way to create AWS Virtual Private Clouds (VPC) with customizable subnets and optional features like NAT Gateways and VPN Gateways. It's built using the AWS Cloud Development Kit (CDK) and allows for the creation of public, private, and isolated subnets according to your specifications.

## Prerequisites

Before you can use the `EnhancedVPC` construct, make sure you have the following prerequisites installed:

- [Node.js](https://nodejs.org/) (with `npm`)
- [AWS CLI](https://aws.amazon.com/cli/)
- [AWS CDK Toolkit](https://docs.aws.amazon.com/cdk/latest/guide/cli.html)

## Installation

To use the `EnhancedVPC` construct in your project, you need to install the AWS CDK libraries for EC2 and the Constructs library. In your project directory, run:

```bash
npm install @aws-cdk/aws-ec2 constructs
```