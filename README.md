# aecid-parsergenerator
Automatically create parser trees for textual logdata to facilitate analysis

To get started, just clone this repository and execute
```
python3 AECIDpg.py
```
to run the aecid-parsergenerator with the default input file and configurations. To change the configuration, edit the PGConfig.py file.

There are two sample configurations for Exim Mainlog and Audit logs. Just copy either of the configurations by
```
cp configs/PGConfig_exim.py PGConfig.py
```
or
```
cp configs/PGConfig_audit.py PGConfig.py
```
and then execute the main script as before.

The script generates a list of event templates, a parser in tree format, an AMiner parser file, and optionally a visualization of the parser tree. To view the output, use one of
```
cat data/out/GeneratedParserModel.py
cat data/out/logTemplates.txt
cat data/out/tree.txt
```
or open data/out/visualization.png.

More information on the aecid-parsergenerator is provided in the following paper: 
Wurzenberger M., Landauer M., Skopik F., Kastner W. (2019): AECID-PG: A Tree-Based Log Parser Generator To Enable Log Analysis.
4th IEEE/IFIP International Workshop on Analytics for Network and Service Management (AnNet 2019) in conjunction with the IFIP/IEEE International Symposium on Integrated Network Management (IM), April 8, 2019, Washington D.C., USA. IEEE.
Link to PDF: https://www.skopik.at/ait/2019_annet.pdf
