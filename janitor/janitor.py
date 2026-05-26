import boto3
import json
import argparse
from datetime import datetime, timezone
from constants import PRICING, REQUIRED_TAGS

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true", default=True)
parser.add_argument("--delete", action="store_true")
parser.add_argument("--stopped-days", type=int, default=14)
args = parser.parse_args()

ec2 = boto3.client(
    "ec2",
    region_name="us-east-1",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

findings = []

def get_tags(tag_list):
    if not tag_list:
        return {}
    return {t["Key"]: t["Value"] for t in tag_list}

def missing_required(tags):
    return any(tag not in tags for tag in REQUIRED_TAGS)

# EBS volumes
volumes = ec2.describe_volumes()["Volumes"]

for v in volumes:
    if v["State"] == "available":
        tags = get_tags(v.get("Tags", []))
        findings.append({
            "resource_id": v["VolumeId"],
            "resource_type": "ebs_volume",
            "reason": "unattached",
            "age_days": 0,
            "estimated_monthly_cost_usd": v["Size"] * PRICING["ebs_gp3_per_gb"],
            "tags": tags,
            "suggested_action": "delete",
            "safe_to_auto_delete": False
        })

# EC2 instances
reservations = ec2.describe_instances()["Reservations"]

for r in reservations:
    for i in r["Instances"]:
        tags = get_tags(i.get("Tags", []))

        if i["State"]["Name"] == "stopped":
            findings.append({
                "resource_id": i["InstanceId"],
                "resource_type": "ec2_instance",
                "reason": "stopped",
                "age_days": 0,
                "estimated_monthly_cost_usd": PRICING["stopped_instance_monthly"],
                "tags": tags,
                "suggested_action": "terminate",
                "safe_to_auto_delete": False
            })

        if missing_required(tags):
            findings.append({
                "resource_id": i["InstanceId"],
                "resource_type": "ec2_instance",
                "reason": "missing_tags",
                "age_days": 0,
                "estimated_monthly_cost_usd": 0,
                "tags": tags,
                "suggested_action": "tag",
                "safe_to_auto_delete": False
            })

# Elastic IPs
addresses = ec2.describe_addresses()["Addresses"]

for a in addresses:
    if "InstanceId" not in a:
        findings.append({
            "resource_id": a["AllocationId"],
            "resource_type": "elastic_ip",
            "reason": "unassociated",
            "age_days": 0,
            "estimated_monthly_cost_usd": PRICING["eip_monthly"],
            "tags": {},
            "suggested_action": "release",
            "safe_to_auto_delete": False
        })

# Write report
report = {
    "scan_timestamp": datetime.now(timezone.utc).isoformat(),
    "account_id": "000000000000",
    "region": "us-east-1",
    "summary": {
        "total_orphans": len(findings),
        "estimated_monthly_waste_usd": round(sum(f["estimated_monthly_cost_usd"] for f in findings), 2)
    },
    "findings": findings
}

with open("report.json", "w") as f:
    json.dump(report, f, indent=2)

with open("report.md", "w") as f:
    f.write("# Cost Janitor Report\n\n")
    for fnd in findings:
        f.write(f"- {fnd['resource_type']} {fnd['resource_id']} ({fnd['reason']})\n")

print(json.dumps(report, indent=2))

if args.dry_run and findings:
    exit(1)
