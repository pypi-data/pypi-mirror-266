from aws_cdk import aws_ec2 as ec2
from constructs import Construct

class EnhancedVPC(Construct):

    def __init__(self, scope: Construct, id: str,
                 max_azs: int = 2,
                 num_public_subnets: int = 1,
                 num_private_subnets: int = 1,
                 num_isolated_subnets: int = 1,
                 enable_nat_gateway: bool = True,
                 enable_vpn_gateway: bool = False,
                 **kwargs):
        super().__init__(scope, id, **kwargs)

        subnet_configuration = []

        # Public Subnets
        for i in range(num_public_subnets):
            subnet_configuration.append(ec2.SubnetConfiguration(
                name=f"Public{i + 1}",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=24
            ))

        # Private Subnets
        for i in range(num_private_subnets):
            subnet_configuration.append(ec2.SubnetConfiguration(
                name=f"Private{i + 1}",
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                cidr_mask=24
            ))

        # Isolated Subnets
        for i in range(num_isolated_subnets):
            subnet_configuration.append(ec2.SubnetConfiguration(
                name=f"Isolated{i + 1}",
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                cidr_mask=24
            ))

        # Determine the number of NAT Gateways
        nat_gateways = num_public_subnets if enable_nat_gateway else 0

        # Create the VPC
        self.vpc = ec2.Vpc(self, "CustomVPC",
                           max_azs=max_azs,
                           nat_gateways=nat_gateways,
                           subnet_configuration=subnet_configuration)

        # Optionally add a VPN Gateway
        if enable_vpn_gateway:
            ec2.CfnVPNGateway(self, "VPNGateway",
                              type="ipsec.1",
                              amazon_side_asn=64512)

            ec2.CfnVPCGatewayAttachment(self, "VPNGatewayAttachment",
                                        vpc_id=self.vpc.vpc_id,
                                        vpn_gateway_id=self.node.find_child("VPNGateway").ref)

