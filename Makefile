CURRENT_PATH = $(shell pwd)
BUILD_PATH = $(CURRENT_PATH)/build

SUBDIRS := $(wildcard */.)
PLATFORMS := darwin-arm64 darwin-amd64 linux-amd64 linux-armv7 linux-arm64 linux-x86 windows-amd64 windows-x86

.PHONY: all
all: 
	for dir in $(SUBDIRS); do \
		if [ -f $$dir/Makefile ];then \
			$(MAKE) -C $$dir; \
		fi; \
	done

.PHONY: package
package:
	mkdir -pv $(BUILD_PATH)
	for dir in $(SUBDIRS); do \
		if [ -f $$dir/Makefile ];then \
			cp -v -r -p $$dir/build/* $(BUILD_PATH); \
		fi; \
	done
	cp -rpv $(CURRENT_PATH)/activate.sh $(BUILD_PATH)/activate 
	chmod a+x $(BUILD_PATH)/activate

.PHONY: clean
clean:
	for dir in $(SUBDIRS); do \
		if [ -f $$dir/Makefile ];then \
			$(MAKE) -C $$dir clean; \
		fi; \
	done
	rm -rf $(BUILD_PATH)
