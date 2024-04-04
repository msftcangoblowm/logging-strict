.ONESHELL:
SHELL := /bin/bash

# Minimal makefile for Sphinx documentation
#

#virtual environment. If 0 issue warning
#Not activated:0
#activated: 1
ifeq ($(VIRTUAL_ENV),)
$(warning virtualenv not activated)
is_venv =
else
is_venv = 1
VENV_BIN := $(VIRTUAL_ENV)/bin
VENV_BIN_PYTHON := python3
endif

err_check_web_conn := Failed. Has issues or no web connection

# You can set these variables from the command line.
SPHINXOPTS    := -aE
SPHINXBUILDNOOPT := $(VENV_BIN)/sphinx-build
SPHINXBUILD   := $(SPHINXBUILDNOOPT) $(SPHINXOPTS) $(O)
SOURCEDIR     := .
BUILDDIR      := _build

##@ Build

.PHONY: html
html:				## Sphinx build html. Only whats been changed
ifeq ($(is_venv),1)
	@$(SPHINXBUILDNOOPT) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html"
endif

.PHONY: htmlall
htmlall:				## Sphinx build clean and build html
ifeq ($(is_venv),1)
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html"
endif

# @$(SPHINXBUILD) -b latexpdf "$(SOURCEDIR)" "$(BUILDDIR)/latex"
.PHONY: pdf
pdf:				## Sphinx build pdf
ifeq ($(is_venv),1)
	@$(SPHINXBUILDNOOPT) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)"

endif

##@ Test

.PHONY: linkcheck
linkcheck:				## Sphinx check urls within docs and code base
ifeq ($(is_venv),1)
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" || echo "$(err_check_web_conn). exit code $$?"
endif

# sphobjinv convert -q zlib objects-black.txt objects-black.inv
# sphobjinv convert -q zlib objects-logging-strict.txt objects-logging-strict.inv
# sphobjinv convert -q zlib objects-setuptools-scm.txt objects-setuptools-scm.inv
# sphobjinv convert -q zlib objects-strictyaml-source.txt objects-strictyaml-source.inv
# sphobjinv convert -q zlib objects-strictyaml-docs.txt objects-strictyaml-docs.inv
# sphobjinv convert -q zlib objects-textual-docs.txt objects-textual-docs.inv
.PHONY: _objects
_objects:
ifeq ($(is_venv),1)
	@if [[ -n "$(project_name)" ]] && [[ -z "$(find)" ]]; then

	echo "$(usage)" 1>&2

	else

	if [[ ! -x $(VENV_BIN)/sphobjinv ]]; then
	echo "package sphobjinv not installed or available"
	else
	objinv=objects-$(project_name).inv
	/bin/yes | $(VENV_BIN)/sphobjinv suggest $(SOURCEDIR)/$$objinv "$(find)" -st 58
	fi

	fi
endif

# make objects_py find=logging.Logger
# $(VENV_BIN_PYTHON) -m sphinx.ext.intersphinx $(SOURCEDIR)/objects-python.inv
.PHONY: objects_py
objects_py: override project_name := python
objects_py: override usage := "make objects_py find=[dotted path]"
objects_py:	_objects		## Query python Sphinx objects. make objects_py find="[dotted path]"
objects_py:

# $(VENV_BIN_PYTHON) -m sphinx.ext.intersphinx $(SOURCEDIR)/objects-logging-strict.inv
# make objects_strict find=VERSION_FALLBACK
.PHONY: objects_strict
objects_strict: override project_name := logging-strict
objects_strict: override usage := "make objects_strict find=[dotted path]"
objects_strict:	_objects	## Query logging-strict Sphinx objects. make objects_strict find="[dotted path]"
objects_strict:

# make obj_strictyaml find=YAML
# make obj_strictyaml find=strictyaml.exceptions
.PHONY: obj_strictyaml
obj_strictyaml: override project_name := strictyaml
obj_strictyaml: override usage := "make obj_strictyaml find=[dotted path]"
obj_strictyaml:	_objects	## Query strictyaml Sphinx objects. make obj_strictyaml find="[dotted path]"
obj_strictyaml:

# Stubbornly insists on repeating on outdated files.
# -T show tracebacks on Exception
# -q quiet
# --keep-going even if there are warnings
.PHONY: doctest
doctest:				## Confirm in-doc code does what it claims
ifeq ($(is_venv),1)
	@$(MAKE) htmlall
	$(SPHINXBUILDNOOPT) -b doctest "$(SOURCEDIR)" "$(BUILDDIR)"
endif

##@ Misc

# Put it first so that "make" without argument is like "make help".
.PHONY: sphinx_help
sphinx_help:			## sphinx-build --help
ifeq ($(is_venv),1)
	@$(SPHINXBUILD) --help "$(SOURCEDIR)" "$(BUILDDIR)"
endif

# Original
# https://www.thapaliya.com/en/writings/well-documented-makefiles/
# coverage adaptation (https://github.com/nedbat/coveragepy/commits?author=nedbat)
# https://github.com/nedbat/coveragepy/blob/5124586e92da3e69429002b2266ce41898b953a1/Makefile
.PHONY: help
help:				## (Default) Display this help -- Always up to date
	@awk -F ':.*##' '/^[^: ]+:.*##/{printf "  \033[1m%-20s\033[m %s\n",$$1,$$2} /^##@/{printf "\n%s\n",substr($$0,5)}' $(MAKEFILE_LIST)
	#@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
.PHONY: Makefile
%: Makefile				## Catch all target
ifeq ($(is_venv),1)
	@$(SPHINXBUILD) -b $@ "$(SOURCEDIR)" "$(BUILDDIR)"
endif
