#Copyright 2018 iRobot Corporation
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

SHELL = /bin/bash
#FOO = $(eval FOO := expensive-to-evaluate)$(FOO)

$(if $(BUILD_DIR),,$(error BUILD_DIR required))

PYTHON := python$(PYTHON_VERSION)

printvar = @echo $(1):	$($(1))
printfn = @echo $(1):	$(call $(1),$(FUNC_NAME))

get_files = $(addprefix $(1)/,$(shell find $(1) -name ".*" -prune -o -name tests -prune -o -name build -prune -o -type f -printf "%P\n"))

func_src_dir = $(DIR_$(1))
func_src_files = $(SRC_FILES_$(1))

func_build_dir = $(BUILD_DIR)/$(1)
func_build_src_dir = $(call func_build_dir,$(1))/src

func_zip_file = $(call func_build_dir,$(1))/code.zip

func_zip_hash_file = $(call func_build_dir,$(1))/zip_hash

func_cloud_code_key = lambda/code/$(1)/$$$$(cat $(call func_zip_hash_file,$(1)))

func_upload_config = $(call func_build_dir,$(1))/$(UPLOAD_CONFIG_FILE_NAME)

func_cloud_hash_file = $(call func_build_dir,$(1))/cloud_hash

func_deploy_name = $(FUNC_DEPLOY_NAME_$(1))

#call as func_name,code_uri[,func_deploy_name]
define setup_func_vars =
$(eval DIR_$(1) := $(2));
$(eval SRC_FILES_$(1) := $(call get_files,$(2)));
$(eval FUNC_DEPLOY_NAME_$(1) := $(if $(3),$(3),$(1)))
endef

define setup_func_targets =
$(call func_zip_file,$(1)): $(2) $(call func_src_files,$(1))
	@mkdir -p $(call func_build_src_dir,$(1))
	@rsync -a --exclude ".*" $(call func_src_dir,$(1))/ $(call func_build_src_dir,$(1))/
	@cd $(call func_build_src_dir,$(1)) && if [ -e requirements.txt ]; then pip install -r requirements.txt -t . -U --upgrade-strategy only-if-needed; fi
	@cd $(call func_build_src_dir,$(1)) && if [ -e Makefile ]; then make; fi
	@cd $(call func_build_src_dir,$(1)) && zip -rq9 $(abspath $(call func_zip_file,$(1))) *

$(call func_zip_hash_file,$(1)): $(2) $(call func_zip_file,$(1))
	@openssl dgst -sha256 -binary $(call func_zip_file,$(1)) | openssl enc -base64 > $(call func_zip_hash_file,$(1))

.PHONY: build/$(1)
build/$(1): $(2) $(call func_zip_file,$(1)) $(call func_zip_hash_file,$(1))

.PHONY: upload/$(1)/config
upload/$(1)/config: $(2) build/$(1)
	@BUCKET=$(BUCKET) && \
	KEY=$(call func_cloud_code_key,$(1)) && \
	printf '{"Bucket": "%s", "Key": "%s"}' \
	$$$$BUCKET \
	$$$$KEY \
	> $(call func_upload_config,$(1))

.PHONY: upload/$(1)
upload/$(1): $(2) build/$(1) upload/$(1)/config
	@BUCKET=$$$$(cat $(call func_upload_config,$(1)) | jq -r '.Bucket') && \
	KEY=$$$$(cat $(call func_upload_config,$(1)) | jq -r '.Key') && \
	if ! aws $(AWS_ARGS) s3api head-object --bucket $$$$BUCKET --key $$$$KEY > /dev/null 2>&1; then \
	  aws $(AWS_ARGS) s3 cp "$(call func_zip_file,$(1))" "s3://$$$$BUCKET/$(call func_cloud_code_key,$(1))"; \
	else \
	  echo File is already uploaded; \
	fi;
	
	@#TODO: indexing

.PHONY: deploy/$(1)
deploy/$(1): $(2) upload/$(1)
	@aws $(AWS_ARGS) lambda get-function --function-name $(1) > $(call func_build_dir,$(1))/deployed_config 2> $(call func_build_dir,$(1))/deployed_config.err; \
	if [ -z $(call func_build_dir,$(1))/deployed_config.err ]; then \
	  cat $(call func_build_dir,$(1))/deployed_config | jq -r '.Configuration.CodeSha256' > $(call func_cloud_hash_file,$(1)); \
	elif grep -q "[^:]*ResourceNotFoundException" $(call func_build_dir,$(1))/deployed_config.err; then \
	  echo 0 > $(call func_cloud_hash_file,$(1)); \
	else \
	  sed -e '/^$/d' $(call func_build_dir,$(1))/deployed_config.err && false; \
	fi;
	rm -f $(call func_build_dir,$(1))/deployed_config*
	
	@if ! cmp --silent $(call func_zip_hash_file,$(1)) $(call func_cloud_hash_file,$(1)); then \
	  echo "Function needs to be updated"; \
	  echo "(TODO: deploy not implemented yet)"; \ 
	else \
	  echo Function is up-to-date; \
	fi;

.PHONY: clean/$(1)
clean/$(1): $(2)
	-rm -rf $(call func_build_dir)
endef # setup_func_targets

#CONFIG={"logical_id_example": {"CodeUri": "./example"}}

$(info config $(CONFIG))

FUNC_NAMES:=$(shell if [ -n "$(CONFIG)" ]; then echo '$(CONFIG)' | jq -r 'to_entries | map(.key) | join(" ")'; fi)

get_config_field=$(if $(findstring LogicalId,$(1)),$(1),$(shell echo '$(CONFIG)' | jq -r '.$(1).$(2) // empty'))

$(foreach func_name,$(FUNC_NAMES),$(call setup_func_vars,$(func_name),$(call get_config_field,$(func_name),CodeUri),$(call get_config_field,$(func_name),FunctionName)))
$(foreach func_name,$(FUNC_NAMES),$(eval $(call setup_func_targets,$(func_name),require_config)))

REQUIRE_CONFIG = $(if $(CONFIG),,$(error CONFIG required))
.PHONY: require_config
require_config:
	$(REQUIRE_CONFIG)

REQUIRE_BUCKET = $(if $(BUCKET),,$(error BUCKET required))
.PHONY: require_bucket
require_bucket:
	$(REQUIRE_BUCKET)

REQUIRE_UPLOAD_CONFIG = $(if $(UPLOAD_CONFIG_FILE_NAME),,$(error UPLOAD_CONFIG_FILE_NAME required))$(if $(MERGED_UPLOAD_CONFIG_FILE),,$(error MERGED_UPLOAD_CONFIG_FILE required))
.PHONY: require_upload_config
require_upload_config:
	$(REQUIRE_UPLOAD_CONFIG)

.PHONY: build
build: $(addprefix build/,$(FUNC_NAMES))

.PHONY: merge_upload_config
merge_upload_config: require_upload_config
	$(PYTHON) -c "from lambda_packager import upload_config; upload_config.merge_upload_config_main()" -o $(MERGED_UPLOAD_CONFIG_FILE) $(foreach func_name,$(FUNC_NAMES),-i $(func_name) $(call func_upload_config,$(func_name))) 

.PHONY: upload
upload: require_bucket $(addprefix upload/,$(FUNC_NAMES)) merge_upload_config

.PHONY: deploy
deploy: require_bucket $(addprefix deploy/,$(FUNC_NAMES))

.PHONY: clean
clean:
	-rm -rf $(BUILD_DIR)

.DEFAULT_GOAL = err
.PHONY: err
err:
	echo this should not happen