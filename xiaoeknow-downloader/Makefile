CURRENT_PATH=$(shell pwd)

.PHONY: generate-requirements
generate-requirements:
	pip3 install pipreqs
	pipreqs $(CURRENT_PATH)  --print | grep -v setuptools  |grep -v pip > $(CURRENT_PATH)/requirements.txt
