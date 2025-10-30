import pulumi
import pulumi_aws as aws

ecr_repository = aws.ecr.Repository(
    "ort-cbd-int-data-in-ecr-repository",
    encryption_configurations=[
        aws.ecr.RepositoryEncryptionConfigurationArgs(
            encryption_type="AES256",
        )
    ],
    image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
        scan_on_push=False,
    ),
    image_tag_mutability="MUTABLE",
    name="ort-cbd-int-data-in",
    opts=pulumi.ResourceOptions(protect=True),
)
