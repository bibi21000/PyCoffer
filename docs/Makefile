# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= ../venv/bin/sphinx-build
SOURCEDIR     = .
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

dev/adaptaters.rst:
	cat dev/adaptaters/header >dev/adaptaters.rst
	cat dev/adaptaters/Yubico_YubiKey_OTP+FIDO+CCID_1050_0407 >>dev/adaptaters.rst
	cat dev/adaptaters/ExcelSecu_FIDO2_Security_Key_1ea8_fc25 >>dev/adaptaters.rst
	cat dev/adaptaters/ExcelSecu_FIDO2_Security_Key_1ea8_fc26 >>dev/adaptaters.rst
	cat dev/adaptaters/FS_ePass_FIDO_096e_0853 >>dev/adaptaters.rst
	cat dev/adaptaters/NEOWAVE_NEOWAVE_Winkeo_FIDO2_1e0d_f1d0 >>dev/adaptaters.rst
	cat dev/adaptaters/footer >>dev/adaptaters.rst

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
