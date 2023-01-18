# note: call scripts from /scripts
CURRENT_PATH				:= $(shell pwd)
APP_NAME					:= fix-git-username-email
BUILD_DIR					:= $(CURRENT_PATH)/build

.PHONY:all
all:
	mkdir -pv $(BUILD_DIR)/noarch
	cp $(CURRENT_PATH)/fix-git-username-email.sh $(BUILD_DIR)/noarch/$(APP_NAME)
	chmod a+x $(BUILD_DIR)/noarch/$(APP_NAME)

.PHONY: clean
clean:
	@rm -rf ${BUILD_DIR} > /dev/null 2>&1 < /dev/null || echo ""
