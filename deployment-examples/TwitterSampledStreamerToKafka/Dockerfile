# Inspired by:
#   https://pythonspeed.com/articles/faster-multi-stage-builds/
# from https://gist.github.com/operatorequals/a1264ad67b3b9a08651c9736bbfe26b0
FROM python:3.7-slim as compile-image

# Install all cython and C toolchain
#   Save some space from the compile-image by apt-cleaning and deleting
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc cython3 python3-dev \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /root
# ----
COPY TwitterSampledStreamerToKafka.py .
COPY ednaconf.yaml .
# Extra
COPY setup.py .
COPY setup.cfg .
COPY ./src ./src/
RUN pip install --user .
# ----

# Transpile 'main.py' to 'main.c'
RUN cython3 -3 --embed -o TwitterSampledStreamerToKafka.c TwitterSampledStreamerToKafka.py
# Compile 'main.c' to an 'main' ELF 
RUN gcc -Os -I /usr/include/python3.7m -o TwitterSampledStreamerToKafka TwitterSampledStreamerToKafka.c -lpython3.7m -lpthread -lm -lutil

# Use different image for runtime
FROM python:3.7-slim as runtime-image
# Extra
COPY --from=compile-image /root/.local /root/.local


# Create non-root user (Security First!)
#RUN useradd --create-home ebka-TwitterSampledStreamerToKafka
#WORKDIR /home/ebka-TwitterSampledStreamerToKafka
#USER ebka-TwitterSampledStreamerToKafka
WORKDIR /root

# Copy 'main' executable to a brand new Python3.7m image (it has to be linked against 'python3.7m')
COPY --from=compile-image /root/TwitterSampledStreamerToKafka /root/ednaconf.yaml /root/

# Use it as entrypoint
CMD [ "./TwitterSampledStreamerToKafka" ]