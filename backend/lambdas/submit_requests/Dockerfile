FROM public.ecr.aws/lambda/python:3.12

COPY models/ ${LAMBDA_TASK_ROOT}/models
COPY lambdas/submit_requests/handler.py ${LAMBDA_TASK_ROOT}

CMD ["handler.handler"]
