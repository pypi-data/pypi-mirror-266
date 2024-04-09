from ._preprocessing import Preprocessor


class FunctionTransformer(Preprocessor):
    #TODO CustomTransformer, evtl übersetzen der gängisten np. funktionen in sql
    # TODO: create and add to _transform
    pass

class KBinsDiscretizer(Preprocessor):
    """
    Bin continuous data into intervals.
    vorhanden über FixedWidthBinning und VariableWidthBinning (quantiles)
    aber nur: enccode ordinal (nicht onehot)
    fehlend: strategy = 'kmeans' --> in VariableWidthBinning einbauen
    """
    #TODO: kmeans, check TD function or use numpy function, only ordinal supported
    #TODO: create and add to _discritze
    pass





class Normalizer(Preprocessor):
    """
    preprocessing.Normalizer([norm, copy])
        Normalize samples individually to unit norm.
        eher unwichtig
    """
    # TODO: create and add to _transform
    pass



class OneHotEncoder(Preprocessor):
    """
	Encode categorical features as a one-hot numeric array.
	wichtig, aber noch nicht umgesetzt, paarameter sind
	categories = 'auto' or list
	handle_unknown = infrequent_if_exist
	min_frequency, max_categories
    """
    #TODO: umsetzen and add to _features
    pass

class OrdinalEncoder(Preprocessor):
    """
    preprocessing.OrdinalEncoder(*[, ...])
	Encode categorical features as an integer array.
	vorhanden LabelEncoder, aber funktioniert bisher nur mit Varchar
    """
    # TODO: create wrapper for LabelEncoder with __new__ and add to _discretise
    pass





class PowerTransformer(Preprocessor):
    """
    preprocessing.PowerTransformer([method, ...])
	Apply a power transform featurewise to make data more Gaussian-like.
	nicht vohranden, fitting lokal nötig, da ein lambda parameter mit max likelihood geschätzt werden muss
	https://scikit-learn.org/stable/modules/preprocessing.html#mapping-to-a-gaussian-distribution
	"""
    # TODO: fitting local and add to _features
    pass


"""
Concat
MultiColSum
CustomTransformerMultiCol

KernelPCA
PCA
SparsePCA
GaussianRandomProjection
SparseRandomProjection
"""



