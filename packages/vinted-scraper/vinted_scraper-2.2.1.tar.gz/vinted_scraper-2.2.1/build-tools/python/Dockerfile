FROM python:3.10.12-slim AS base_image

FROM base_image AS builder

WORKDIR /tmp

COPY ./requirements.txt .

ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NOWARNINGS="yes"

RUN useradd -ms /bin/bash installer

USER installer
RUN python3 -m pip install --user --no-warn-script-location --no-cache-dir --disable-pip-version-check -r requirements.txt

FROM base_image AS release

ENV PATH /home/app/.local/bin:$PATH

ENTRYPOINT ["python3"]
CMD ["-m", "src.main"]

RUN useradd -ms /bin/bash app
USER app

COPY --from=builder /home/installer/.local /home/app/.local
COPY ./src /usr/src/app/src

WORKDIR /usr/src/app
