FROM public.ecr.aws/lambda/python:3.12

ARG LAMBDA_DIR

COPY models/ ${LAMBDA_TASK_ROOT}/models
COPY auth.py ${LAMBDA_TASK_ROOT}/auth.py
COPY lambdas/${LAMBDA_DIR}/handler.py ${LAMBDA_TASK_ROOT}

CMD ["handler.handler"]