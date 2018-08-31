from owlready2 import *
import os
import textwrap


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
    class is_mentioned_in(ObjectProperty):
        domain = [breast_implant_device]
        range = [fda_pma_submission_supplement]
    class mentions(ObjectProperty):
        domain = [fda_pma_submission_supplement]
        range = [breast_implant_device]
        inverse_property = is_mentioned_in


    # ------- DATA PROPERTIES ---------
    positiveFloat = ConstrainedDatatype(float, min_exclusive=0)

    class has_diameter(DataProperty):
        range = [positiveFloat]
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
    class catalogNumber(AnnotationProperty): pass
    class deviceID(AnnotationProperty): pass
    class versionModelNumber(AnnotationProperty): pass
    class devicePublishDate(AnnotationProperty): pass
    class deviceDescription(AnnotationProperty): pass
    class gudidLink(AnnotationProperty): pass
    class pmaLink(AnnotationProperty): pass
    class gmdnPTName(AnnotationProperty): pass
    class gmdnPTDefinition(AnnotationProperty): pass

    class pmaApprovalOrderStatement(AnnotationProperty): pass
    class pmaGenericName(AnnotationProperty): pass
    class pmaSupplementType(AnnotationProperty): pass
    class pmaSupplementReason(AnnotationProperty): pass
    class pmaTradeName(AnnotationProperty): pass
    class pmaApplicant(AnnotationProperty): pass
    class pmaApplicantAddress(AnnotationProperty): pass
    class pmaDateRecieved(AnnotationProperty): pass
    class pmaDecisionDate(AnnotationProperty): pass
    class pmaDecisionCode(AnnotationProperty): pass
    class pmaReviewGranted(AnnotationProperty): pass
    class pmaAdvisoryCommitee(AnnotationProperty): pass
    class pmaDocketNumber(AnnotationProperty): pass
    class pmaFedRegNoticeDate(AnnotationProperty): pass

    # -- W3 annotations --
    class skosAltLabel(AnnotationProperty): pass
    class skosDefinition(AnnotationProperty): pass

    alt_label = onto.search_one(iri="*skosAltLabel")
    alt_label.iri = 'http://www.w3.org/2004/02/skos/core#altLabel'
    alt_label.label = 'skos:altLabel'
    alt_label.python_name = 'alt_label'

    definition = onto.search_one(iri="*skosDefinition")
    definition.iri = 'http://www.w3.org/2004/02/skos/core#definition'
    definition.label = 'skos:definition'
    definition.python_name = 'definition'


    # ------ CLASS DEFINITIONS ----------
    class silicone_gel_filled_breast_implant(breast_implant_device):
        equivalent_to = [breast_implant_device &
                         has_filling.some(silicone_gel_filling)]
    class saline_filled_breast_implant(breast_implant_device):
        equivalent_to = [breast_implant_device &
                         has_filling.some(saline_filling)]
    class smooth_breast_implant(breast_implant_device):
        equivalent_to = [breast_implant_device &
                         has_shell_surface.some(smooth_shell_surface)]
    class textured_breast_implant(breast_implant_device):                    
        equivalent_to = [breast_implant_device &
                         has_shell_surface.some(textured_shell_surface)]
    # class smooth_silicone_breast_implant(breast_implant_device):
    #     equivalent_to = [breast_implant_device &
    #                      has_shell_surface.some(smooth_shell_surface) &
    #                      has_filling.some(silicone_gel_filling)]
    # class smooth_saline_breast_implant(breast_implant_device):
    #     equivalent_to = [breast_implant_device &
    #                      has_shell_surface.some(smooth_shell_surface) &
    #                      has_filling.some(saline_filling)]
    # class textured_silicone_breast_implant(breast_implant_device):
    #     equivalent_to = [breast_implant_device &
    #                      has_shell_surface.some(textured_shell_surface) &
    #                      has_filling.some(silicone_gel_filling)]
    # class textured_saline_breast_implant(breast_implant_device):
    #     equivalent_to = [breast_implant_device &
    #                      has_shell_surface.some(textured_shell_surface) &
    #                      has_filling.some(saline_filling)]

    # --------- ANNOTATIONS --------------
    bi_device = onto.search_one(iri="*breast_implant_device")

    bi_device.definition = ("Breast implants are medical devices that are implanted under the breast tissue or under "
                            "the chest muscle to increase breast size (augmentation) or to rebuild breast tissue "
                            "after mastectomy or other damage to the breast (reconstruction). They are also used in "
                            "revision surgeries, which correct or improve the result of an original surgery.")

    bi_device.isDefinedBy = ("https://www.fda.gov/medicaldevices/productsandmedical"
                             "procedures/implantsandprosthetics/breastimplants/default.htm")

onto.save()
