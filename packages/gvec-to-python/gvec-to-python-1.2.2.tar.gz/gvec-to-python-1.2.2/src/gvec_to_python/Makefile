#--------------------------------------
# CONFIGURATION
#--------------------------------------

PYTHON  := python3
SO_EXT  := $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
LIBDIR  := $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))")
install_path := $(shell $(PYTHON) -c "import gvec_to_python as _; print(_.__path__[0])")

FLAGS            := --libdir $(LIBDIR) $(flags) 

#--------------------------------------
# SOURCE FILES 
#--------------------------------------

# Splines
BK   := $(install_path)/hylife/utilities_FEEC/bsplines_kernels
BEV1 := $(install_path)/hylife/utilities_FEEC/basics/spline_evaluation_1d

SOURCES := $(BK).py $(BEV1).py 

OUTPUTS := $(SOURCES:.py=$(SO_EXT))

#--------------------------------------
# PYCCELIZE
#--------------------------------------

.PHONY: all
all: $(OUTPUTS)

$(BK)$(SO_EXT) : $(BK).py
	pyccel $(FLAGS) $< 

$(BEV1)$(SO_EXT) : $(BEV1).py $(BK)$(SO_EXT)
	pyccel $(FLAGS) $< 

#--------------------------------------
# CLEAN UP
#--------------------------------------

.PHONY: clean
clean:
	rm -rf $(OUTPUTS)
    
	find . -type d -name '__pyccel__' -prune -exec rm -rf {} \;
	find . -type d -name '__pycache__' -prune -exec rm -rf {} \;
	find . -type f -name '*.lock' -delete