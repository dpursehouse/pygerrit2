#
# This makefile executes all tests found in the current directory. The
# tests are divided in categories, typically connected to a particular
# script, and the actual testcases are defined in the directory
# <category>/<testcase>.
#
# Each testcase directory can contain the following special files:
#
#    command     A shell script (doesn't have to be executable) that
#                will be invoked by sh to run the testcase.
#    input       Will be fed to the stdin stream of the command script.
#    output      The expected stdout output of the command script.
#                If present, the actual output will be compared to the
#                contents of this file.
#    status      The expected exit status of the command script,
#                expressed as an integer.
#
# In addition to this, users are encouraged to include a file README that
# explains the purpose of the testcase in question.
#
# Command scripts will be run with the parent directory of the
# makefile as current directory (should be the top directory of the
# git). To access files stored in the testcase directory the $TESTDIR
# variable is available.
#
# In addition to the `all' default goal, each test category gets its
# own make goal, i.e. if you have a category (and subdirectory) named
# `mytests', you can run just these tests with `make mytests'.
#

# Only testcases with a `command' file are considered.
ALL_CATEGORIES := \
    $(sort $(foreach t,$(wildcard */*/command),$(firstword $(subst /, ,$(t)))))

.PHONY: all
all: $(ALL_CATEGORIES)
	@echo All tests successful

define create-category
$(eval .PHONY: $(1)
$(1):
	@./test_category.sh $(1) ..
)
endef

$(foreach category,$(ALL_CATEGORIES),\
    $(call create-category,$(category)))
