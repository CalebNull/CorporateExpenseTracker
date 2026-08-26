#!/bin/bash
set -e

REGION="us-east-2"
ACCOUNT_ID="717279721998"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/service-role/submit_requests-role-5sn0b6jq"

aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

FUNCTIONS=(
  "submit_requests"
  "approve_reject"
  "mark_paid"
  "get_requests"
  "budgets"
  "users"
  "get_audit_trail"
  "spending_report"
  "delete_request"
)

for FN in "${FUNCTIONS[@]}"; do
  echo "=== $FN ==="
  IMAGE_NAME="${FN//_/-}-lambda"
  ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${IMAGE_NAME}"

  docker build --provenance=false --sbom=false \
    --build-arg LAMBDA_DIR="$FN" \
    -f Dockerfile \
    -t "$IMAGE_NAME" .

  aws ecr create-repository --repository-name "$IMAGE_NAME" --region "$REGION" 2>/dev/null || echo "repo already exists, continuing"

  docker tag "$IMAGE_NAME:latest" "$ECR_URI:latest"
  docker push "$ECR_URI:latest"

  aws lambda update-function-code \
    --function-name "${FN}_container" \
    --image-uri "$ECR_URI:latest" \
    --region "$REGION" 2>/dev/null || \
  aws lambda create-function \
    --function-name "${FN}_container" \
    --package-type Image \
    --code ImageUri="$ECR_URI:latest" \
    --role "$ROLE_ARN" \
    --region "$REGION"

  echo "=== Done: $FN ==="
done