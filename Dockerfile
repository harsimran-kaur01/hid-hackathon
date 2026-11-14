FROM public.ecr.aws/lambda/python:3.11

# System libs for OpenCV
RUN yum install -y libglib2.0-0 libsm6 libxext6 libxrender1 libgomp \
    && yum clean all

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY models/ ${LAMBDA_TASK_ROOT}/models/
COPY spoof_detector.py ${LAMBDA_TASK_ROOT}
COPY app.py ${LAMBDA_TASK_ROOT}
COPY MiniFASNetV2.pth ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]