# Struturation of the datas

The file hebrew_xml_export.xml is a raw export of the whole Hebrew texts of Ben Sira in a single XML file. Each indesign style has been encoded by an XML tag.
The list of these tags is given and commented in the Hebrew_DTD file.

This single file was been subdivided into nine files representing the nine Hebrew manuscripts of Ben Sira.

**The Cairo genizah manuscripts**
- Ms_a
- Ms_b
- Ms_c
- Ms_d
- Ms_e
- Ms_f

**The Qumran and Masada Scrolls**
- Ms_2Q18
- Ms_11QPsa
- MS_Massada

For parsing, some tags can be ignored:
- <col>, <vacat_prg>, <vacat_car>, <folio>, <line>, <greek>, <reconstructed>, <margin_reconstructed> 
- As a first step, can also be ignorer the tags : <superscript>, <supralinear>, <margin_infralinear> and <margin_supralinear>.

Other tags can be merged (or considered similar):
- <margin>, <margin_right>, <margin_left>, <margin_car>