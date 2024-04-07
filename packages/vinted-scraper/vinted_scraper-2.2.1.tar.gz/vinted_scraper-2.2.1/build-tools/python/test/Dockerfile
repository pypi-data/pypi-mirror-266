FROM test-base-image:tmp AS base_image

ENTRYPOINT ["python3"]
CMD ["-m", "unittest", "discover"]

COPY . /usr/src/app/src