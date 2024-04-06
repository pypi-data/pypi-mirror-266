import json

from allotropy.parser_factory import Vendor
from allotropy.to_allotrope import allotrope_from_file

if __name__ == "__main__":
    for output_file in (
        # "appbio_quantstudio_designandanalysis_QS1_Standard_Curve_example01.xlsx",
        # "appbio_quantstudio_designandanalysis_QS3_Relative_Quantification_example02.xlsx",
        # "appbio_quantstudio_designandanalysis_QS5_Standard_Curve_4Plex_example03.xlsx",
        # "appbio_quantstudio_designandanalysis_QS6_Standard_Curve_example04.xlsx",
        # "appbio_quantstudio_designandanalysis_QS6Pro_Standard_Curve_example05.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7_Standard_Curve_example06.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7Pro_Genotyping_example07.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7Pro_Multiplex_example08.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7Pro_PCR_with_Melt_example09.xlsx",
        "appbio_quantstudio_designandanalysis_QS7Pro_Presence_and_Absence_example10.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7Pro_Relative_Quantification_example11.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7Pro_Relative_Quantification_Biogroup_example12.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7Pro_Relative_Standard_Curve_example13.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7Pro_Standard_Curve_example14.xlsx",
        # "appbio_quantstudio_designandanalysis_QS7Pro_Standard_Curve_TAC_example15.xlsx",
        # "appbio_quantstudio_designandanalysis_OpenArray_GeneExp_example16.xlsx",
        # "appbio_quantstudio_designandanalysis_OpenArray_Genotyping_example17.xlsx",
        # "example.xlsx",
    ):
        test_filepath = f"../tests/parsers/appbio_quantstudio_designandanalysis/testdata/{output_file}"
        allotrope_dict = allotrope_from_file(
            test_filepath, Vendor.APPBIO_QUANTSTUDIO_DESIGNANDANALYSIS
        )
        print(json.dumps(allotrope_dict, indent=4, ensure_ascii=False))  # noqa: T201
