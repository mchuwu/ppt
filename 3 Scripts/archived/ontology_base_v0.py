from owlready2 import *
import os
import textwrap


#          FDA PMA NUMBER -> PMA SUPPLEMENT NUMBER
#           V
# ADD PMA SUBMISSION is subject device of DEVICE
# NOM FILL, MIN FILL, MAX FILL

onto_path.append("1 Ontology/")
onto = get_ontology("http://purl.obolibrary.org/BIO/breast_implant_ontology_base.owl")
onto.base_iri = "http://purl.obolibrary.org/BIO/"

# ------- SETTINGS --------

# render entities using label
def render_using_label(entity):
    return entity.label.first() or entity.name
set_render_func(render_using_label)


with onto:
    # ------- CLASSES ---------
    class breast_implant_device(Thing): pass
    # class breast_implant_brand(Thing): pass
    class breast_implant_filling(Thing): pass
    class breast_implant_manufacturer(Thing): pass
    class breast_implant_product_code(Thing): pass
    class breast_implant_profile(Thing): pass

    class fda_medical_device_submission(Thing): pass
    class fda_pma_submission(fda_medical_device_submission): pass
    class fda_pma_submission_supplement(fda_medical_device_submission): pass

    class breast_implant_shape(Thing): pass
    class breast_implant_shell(Thing): pass
    class breast_implant_shell_surface(Thing): pass
    class breast_implant_style(Thing): pass

    class saline_filling(breast_implant_filling): pass
    class silicone_gel_filling(breast_implant_filling): pass

    class round_shape(breast_implant_shape): pass
    class non_round_shape(breast_implant_shape): pass

    class silicone_shell(breast_implant_shell): pass

    class smooth_shell_surface(breast_implant_shell_surface): pass
    class textured_shell_surface(breast_implant_shell_surface): pass

    # ------- OBJECT PROPERTIES -------
    class has_filling(ObjectProperty):
        domain = [breast_implant_device]
        range = [breast_implant_filling]
    class has_manufacturer(ObjectProperty):
        domain = [breast_implant_device]
        range = [breast_implant_manufacturer]
    class has_profile(ObjectProperty):
        domain = [breast_implant_device]
        range = [breast_implant_profile]
    class has_shape(ObjectProperty):
        domain = [breast_implant_device]
        range = [breast_implant_shape]
    class has_shell(ObjectProperty):
        domain = [breast_implant_device]
        range = [breast_implant_shell]
    class has_shell_surface(ObjectProperty):
        domain = [breast_implant_device]
        range = [breast_implant_shell_surface]
    class has_product_code(ObjectProperty):
        domain = [breast_implant_device]
        range = [breast_implant_product_code]
    class has_subject_device(ObjectProperty):
        domain = [fda_pma_submission]
        range = [breast_implant_device]
    class is_subject_device_of(ObjectProperty):
        domain = [breast_implant_device]
        range = [fda_pma_submission]
        inverse_property = has_subject_device
    class has_pma_supplement(ObjectProperty):
        domain = [breast_implant_device]
        range = [fda_pma_submission_supplement]
    class is_pma_supplement_of(ObjectProperty):
        domain = [fda_pma_submission_supplement]
        range = [breast_implant_device]
        inverse_property = has_pma_supplement

    # ------- DATA PROPERTIES ---------
    positiveInteger = ConstrainedDatatype(int, min_exclusive=0)

    class has_diameter(DataProperty):
        range = [positiveInteger]
    class has_fill_volume(DataProperty): pass
    class has_height(DataProperty): pass
    class has_projection(DataProperty): pass
    class has_width(DataProperty): pass

    class has_nominal_fill_volume(has_fill_volume): pass
    class has_max_fill_volume(has_fill_volume): pass
    class has_nominal_projection(has_projection): pass
    class has_max_projection(has_projection): pass
    class has_nominal_diameter(has_diameter): pass
    class has_max_diameter(has_diameter): pass

    # ------ ANNOTATION PROPERTIES -------
    # class altLabel(AnnotationProperty): pass

    class catalogNumber(AnnotationProperty): pass
    class deviceID(AnnotationProperty): pass
    class versionModelNumber(AnnotationProperty): pass
    class devicePublishDate(AnnotationProperty): pass
    class deviceDescription(AnnotationProperty): pass
    class gudidLink(AnnotationProperty): pass
    class pmaLink(AnnotationProperty): pass
    class gmdnPTName(AnnotationProperty): pass
    class gmdnPTDefinition(AnnotationProperty): pass

    class skosAltTerm(AnnotationProperty): pass
    for aprop in onto.annotation_properties():
        if str(aprop) == 'skosAltTerm':
            aprop.name = 'skos:altTerm'
            aprop.iri = "http://www.w3.org/2004/02/skos/core#altLabel"

    # ------ CLASS DEFINITIONS ----------
    class silicone_gel_filled_device(breast_implant_device):
        equivalent_to = [breast_implant_device &
                         has_filling.some(silicone_gel_filling)]
    class saline_filled_device(breast_implant_device):
        equivalent_to = [breast_implant_device &
                         has_filling.some(saline_filling)]
    class smooth_device(breast_implant_device):
        equivalent_to = [breast_implant_device &
                         has_shell_surface.some(smooth_shell_surface)]
    class textured_device(breast_implant_device):                    
        equivalent_to = [breast_implant_device &
                         has_shell_surface.some(textured_shell_surface)]

onto.save()
