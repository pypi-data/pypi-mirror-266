
# basics
import os
import numpy as np
import pandas
from scipy.stats import median_abs_deviation

# special
from pysnid import snid

# in package
from .spectroscopy import Spectrum


SNIDPARSE_TYPING = {"snia": "Ia",
                    "snia-norm": "Ia-norm",
                    "snia-pec-91t": "Ia-91T",
                    "snia-pec-91bg": "Ia-91bg",
                    "snia-pec": "!Ia-norm,Ia-91T,Ia-91bg",
                    }

INSTRUMENT_ZOFFSET = pandas.Series({"SEDm":-0.0010}, name="zoffset")
INSTRUMENT_ZOFFSET.index.name = "instrument"


# Special cases
RM_TYPING_REDSHIFT = ["ZTF19abcttsc", "ZTF19abzlsbl", "ZTF19adajqwl", "ZTF20abgfekk", "ZTF20accmutv", 
                     "ZTF20acyroke", "ZTF18absbspk",
                     "ZTF18abhhxcp","ZTF19aahsclk", "ZTF19abzhvxk" # GAL
                      # rest don't need snidauto
                      "ZTF18abhpgje", "ZTF18acaipdc", "ZTF18acajkff", "ZTF20acvbrbv"
                      # Redshift gain by rm
                      "ZTF18aabxrjp",
                      # redshift
                      "ZTF18aahshhp","ZTF18acefgoc", "ZTF18adatosi", "ZTF19abaukyt", "ZTF19acxngol",
                      "ZTF20aaurhzc", "ZTF20abrjmgi", "ZTF20absitlr", "ZTF20ackitai", "ZTF20acquetr",
                      "ZTF20acxdawc", "ZTF20aciwcuz",
                       #  Gal
                      "ZTF18aaisqmw", "ZTF18abuatfp", "ZTF18accvyao", "ZTF18acpuxuh", "ZTF18aczdapb", "ZTF19adcetym",
                      "ZTF20aanaeev", "ZTF20aankixb", "ZTF20acqikeh", "ZTF20acywbes"
                     ]
    
FORCE_SNIA = ["ZTF18actuhrs"]
#
#
#
#
#

def run_snid(spec_or_filepath, redshift=None, t0=None, t0_err=None,
                delta_redshift=0.05,
                delta_phase=4, # for phase
                lbda_range = [3_500, 10_000], 
                rm_spec_edgepixel = 10, verbose=False,
                **kwargs):
    """ """
    if type(spec_or_filepath) is str:
        spectrum = Spectrum.from_filename(spec_or_filepath)
    else:
        spectrum = spec_or_filepath
    
    # update the lbda_range to be the most conservative between spectrum and input lbda_range
    if lbda_range is not None:
        lbda_range = lbda_range.copy()
        lbda_range[0] = np.max([lbda_range[0], int(spectrum.lbda[rm_spec_edgepixel]+1)])
        lbda_range[1] = np.min([lbda_range[1], int(spectrum.lbda[-rm_spec_edgepixel]-1)])
        print(lbda_range)
    
    if t0 is not None:
        phase = spectrum.get_phase(t0, z=redshift, from_target=False) # take the data we give you
    else:
        phase = None
         
            
    if t0_err is not None:
        delta_phase = np.sqrt(delta_phase**2 + t0_err**2)        
        
    if phase is not None:
        print(f"using phase: {phase} ± {delta_phase:.3f}")
        
    return spectrum.fit_snid(lbda_range=lbda_range, 
                            phase=phase, 
                            redshift=redshift, 
                            delta_redshift=delta_redshift, 
                            delta_phase=delta_phase,
                            verbose=verbose, **kwargs)
#
#
#
#
#
def specfiles_to_snidfiles(filepath):
    """ convert spectrum filename to a snid fit filename
    
    Parameters
    ----------
    filepath: str
        path file name
        
    Returns
    -------
    str
    """
    return filepath.replace(".ascii", "_snid.h5")

def parse_filename(filename):
    """ """
    basename = os.path.basename(filename).split(".")[0]        
    to_parse = basename.split("_")[:4]
    return dict(zip(["targetname", "date", "instrument", "version"],to_parse))

def read_target_snidres(ztfname, instrument="*", concat=True, verbose=False):
    """ reads snid.h5 associated to the target name
    
    Parameters
    ----------
    ztfname: str
        name of the ZTF target
        
    Returns
    -------
    DataFrame
        concatenated snid results dataframe 
    """
    from glob import glob
    from .io import IDR_PATH
    
    if instrument is None:
        instrument = "*"
    elif type(instrument) != str: # assumed list
        instrument = f"[{','.join(instrument)}]*"
    
    snid_target = glob( os.path.join(IDR_PATH, "spectra", f"{ztfname}*_{instrument}_*.h5") )
    if verbose:
        print(snid_target)
        
    sres = [snid.SNIDReader.from_filename(filename).results 
            for filename in snid_target]
    keys = [parse_filename(filename)["instrument"] for filename in snid_target]
    if len(sres) < 1 :
        return None
    
    if not concat:
        return sres
    
    return pandas.concat(sres, keys=keys).reset_index(names=["instrument","no."])

def get_target_snidres(ztfname, 
                        typing=None, rlap_range=[5, None], 
                        n_range=None, grade="good",
                        verbose=False, instrument="*",
                        **kwargs):
    """ get all snid results associated to the target.
    
    Parameters
    ----------
    ztfname: str
        name of the ZTF target

    typing: str
        classification of the target. 
        This is used to select considered snid results entries
        
    rlap_range: None, list
        if not None: [min, max] of the rlap. 
        Use None for no limit, e.g., [5, None] means greater than 5.
        
    n_range: None, list
        if not None: [min, max] of the entry no. 
        Use None for no limit, e.g., [None, 10] means first 10th entries.
        
    grade: None, str, list
        select the grade to considered. If None, no cut.
        
    Returns
    -------
    DataFrame
        concatenated snid results dataframe.
    """
    snidresults = read_target_snidres(ztfname, instrument=instrument)
    if snidresults is None:
        return None
    
    # snid typing
    if typing is not None:
        snid_typing = SNIDPARSE_TYPING.get(typing,None)
        if snid_typing is None:
            warnings.warn(f"Could not parse input {typing} typing")
        elif verbose:
            print(f"using snid_typing:{snid_typing} as input typing:{typing}")

    else:
        snid_typing = None
        
    if snid_typing in ["*","all", "any"]:
        snid_typing = None

    elif snid_typing in ["snia", "sn ia", "Ia"]:
        snid_typing = snidresults[snidresults["typing"] == "Ia"]["type"].unique()

    elif snid_typing is not None and "!" in snid_typing:
        not_these = snid_typing.split("!")[-1].split(",")
        snid_typing = snidresults[(snidresults["typing"] == "Ia") & 
                             ~(snidresults["type"].isin(not_these))]["type"].unique()
            
    # else typing is None            
    if snid_typing is not None:
        snidresults = snidresults[snidresults["type"].isin(np.atleast_1d(snid_typing))]        

    #
    # select data to parse
    #
    # - grade
    if grade is not None:
        snidresults = snidresults[snidresults["grade"].isin(np.atleast_1d(grade))]
        
    # - rlap        
    if rlap_range is not None:
        # handles None as no limit
        rlap_range  = rlap_range.copy()
        if rlap_range[0] is None: rlap_range[0] = 0
        if rlap_range[1] is None: rlap_range[1] = np.inf
        snidresults = snidresults[snidresults["rlap"].between(*rlap_range)]
    
    # - nfirst
    if n_range is not None:
        n_range = n_range.copy()
        if n_range[0] is None: n_range[0] = 0
        if n_range[1] is None: n_range[1] = +np.inf
        snidresults = snidresults[snidresults["no."].astype(int).between(*n_range)]
        
        
    return snidresults

def get_target_snidredshift(ztfname, 
                                weight_by="rlap",
                                typing=None, redshift_err="nmad",
                                rlap_range=[5, None], n_range=[None, 30],
                                instrument="*", 
                                snid_offset=0.0013,
                                apply_zoffset=True,
                                flag_issues=True,
                            as_dataframe=False,
                                **kwargs):
    """ 
    Returns
    -------
    list
        (redshift, redshift_err)
    
    """
    sres = get_target_snidres(ztfname, typing=typing, 
                                rlap_range=rlap_range, n_range=n_range, 
                                instrument=instrument,
                                **kwargs)
    if sres is None or len(sres)==0:
        return np.NaN, np.NaN
    
    # correct for instrument offset.
    if apply_zoffset:
        sres = sres.merge(INSTRUMENT_ZOFFSET, on="instrument", how="left"
                         ).fillna({"zoffset":0})
        sres["z"] = sres["z"] + sres["zoffset"]
        
    # correct for snid offset
    if snid_offset is not None:
        sres["z"] -= snid_offset
    
    # Special output
    if as_dataframe:
        return sres
    # Special output    
    
    if weight_by is not None:
        weights = sres[weight_by]
        
    if np.sum(weights)==0:
        print(f"{ztfname} weights=0")
        return np.NaN, np.NaN
    

    redshift = np.average(sres["z"], weights=weights)    
    if redshift_err == "nmad":
        if len(sres) < 3:
            dredshift = np.NaN
        else:
            dredshift = median_abs_deviation(sres["z"])
    else:
        dredshift = getattr(np, redshift_err)(sres)
        
    if flag_issues:
        issue_report = check_for_issues(sres)
        if len(issue_report)>0:
            print(f" {ztfname} ".center(30, "-"))
            print( issue_report )
            print(" end report ".center(30, "-"))
            
    return redshift, dredshift
                            
    
def check_for_issues(snidres):
    """ """
    mean_, median_, std_, nmad_ = snidres["z"].agg([np.mean, np.median, np.std, median_abs_deviation])
    nentries = len(snidres)
    
    issues = []
    # too large scatter
    if nentries < 3:
        issues.append("less than 3 entries")
    else: # otherwise nothing make sense
        if std_ > 0.01:
            issues.append("large STD (>0.01)")

        if std_ > 0.05:
            issues.append("WARNING very large STD (>0.05)")

        if std_ > 5*nmad_:
            issues.append(f"STD {std_:.3f}> 5* nMAD {nmad_:.3f}")
    
    return issues



