SHELL = /bin/bash
BUILD_DIR = ./.build

ACCOUNT:=$(shell aws sts get-caller-identity --query Account | tr -d \")
REGION:=$(shell aws configure list | awk '/region/ { print $$2 }')

ifndef BUCKET
  ifdef BUCKET_SUFFIX
    BUCKET:=$(REGION).$(ACCOUNT).$(BUCKET_SUFFIX)
  else
  	$(error BUCKET not defined)
  endif
endif

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

func_upload_config = $(call func_build_dir,$(1))/upload_config

func_cloud_hash_file = $(call func_build_dir,$(1))/cloud_hash

func_deploy_name = $(FUNC_DEPLOY_NAME_$(1))

#call as func_name,code_uri[,func_deploy_name]
define setup_func_vars =
$(eval DIR_$(1) := $(2));
$(eval SRC_FILES_$(1) := $(call get_files,$(2)));
$(eval FUNC_DEPLOY_NAME_$(1) := $(if $(3),$(3),$(1)))
endef

define setup_func_targets =
$(call func_zip_file,$(1)): $(call func_src_files,$(1))
	@mkdir -p $(call func_build_src_dir,$(1))
	@rsync -a --exclude ".*" $(call func_src_dir,$(1))/ $(call func_build_src_dir,$(1))/
	@cd $(call func_build_src_dir,$(1)) && if [ -e requirements.txt ]; then pip install -r requirements.txt -t . -U --upgrade-strategy only-if-needed; fi
	@cd $(call func_build_src_dir,$(1)) && if [ -e Makefile ]; then make; fi
	@cd $(call func_build_src_dir,$(1)) && zip -rq9 $(abspath $(call func_zip_file,$(1))) *

$(call func_zip_hash_file,$(1)): $(call func_zip_file,$(1))
	@openssl dgst -sha256 -binary $(call func_zip_file,$(1)) | openssl enc -base64 > $(call func_zip_hash_file,$(1))

.PHONY: build/$(1)
build/$(1): $(call func_zip_file,$(1)) $(call func_zip_hash_file,$(1))

.PHONY: upload/$(1)/config
upload/$(1)/config: build/$(1)
	@BUCKET=$(BUCKET) && \
	KEY=$(call func_cloud_code_key,$(1)) && \
	printf '{"Bucket": "%s", "Key": "%s"}' \
	$$$$BUCKET \
	$$$$KEY \
	> $(call func_upload_config,$(1))

.PHONY: upload/$(1)
upload/$(1): build/$(1) upload/$(1)/config
	@BUCKET=$$$$(cat $(call func_upload_config,$(1)) | jq -r '.Bucket') && \
	KEY=$$$$(cat $(call func_upload_config,$(1)) | jq -r '.Key') && \
	if ! aws s3api head-object --bucket $$$$BUCKET --key $$$$KEY > /dev/null 2>&1; then \
	  aws s3 cp "$(call func_zip_file,$(1))" "s3://$$$$BUCKET/$(call func_cloud_code_key,$(1))"; \
	else \
	  echo File is already uploaded; \
	fi;
	
	@#TODO: indexing

.PHONY: deploy/$(1)
deploy/$(1): upload/$(1)
	@aws lambda get-function --function-name $(1) > $(call func_build_dir,$(1))/deployed_config 2> $(call func_build_dir,$(1))/deployed_config.err; \
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
clean/$(1):
	-rm -rf $(call func_build_dir)
endef

.PHONY: config_from_template
config_from_template:
	if [ -z "$(TEMPLATE)" ]; then (>&2 echo "TEMPLATE not specified"); false; fi
	cat $(TEMPLATE) | jq '.Resources | to_entries | map(select(.value.Type == "AWS::Serverless::Function")) | map({key: .key, value: {CodeUri: .value.Properties.CodeUri, FunctionName: (.value.Properties.FunctionName // .key)}}) | from_entries'

#CONFIG={"logical_id_example": {"CodeUri": "./example"}}

ifndef CONFIG
  ifndef CODE_URI
    $(error No CONFIG or CODE_URI given)
  else ifndef NAME
    NAME = $(basename $(CODE_URI))
  endif

  ifneq ($(NAME),$(FUNCTION_NAME))
    CONFIG := {"$(NAME)": {"CodeUri": "$(CODE_URI)", "FunctionName": "$(FUNCTION_NAME)"}}
  else
    CONFIG := {"$(NAME)": {"CodeUri": "$(CODE_URI)"}
  endif
endif

FUNC_NAMES:=$(shell echo '$(CONFIG)' | jq -r 'to_entries | map(.key) | join(" ")')

get_config_field=$(if $(findstring LogicalId,$(1)),$(1),$(shell echo '$(CONFIG)' | jq -r '.$(1).$(2) // empty'))

$(foreach func_name,$(FUNC_NAMES),$(call setup_func_vars,$(func_name),$(call get_config_field,$(func_name),CodeUri),$(call get_config_field,$(func_name),FunctionName)))
$(foreach func_name,$(FUNC_NAMES),$(eval $(call setup_func_targets,$(func_name))))

.PHONY: build
build: $(addprefix build/,$(FUNC_NAMES))

.PHONY: upload
upload: $(addprefix upload/,$(FUNC_NAMES))

.PHONY: deploy
deploy: $(addprefix deploy/,$(FUNC_NAMES))

.PHONY: clean
clean:
	-rm -rf $(BUILD_DIR)

.DEFAULT_GOAL = print_config
.PHONY: print_config
print_config:
	@printf "%-24s %-24s %s\n" LogicalId FunctionName CodeUri
	$(foreach func_name,$(FUNC_NAMES),@printf "%-24s %-24s %-24s\n" $(func_name) "$(if $(call get_config_field,$(func_name),FunctionName),$(call func_deploy_name,$(func_name)))" "$(call func_src_dir,$(func_name))")

