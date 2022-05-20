# aecid-parsergenerator [![Build Status](https://travis-ci.org/ait-aecid/aecid-parsergenerator.svg?branch=master)](https://travis-ci.org/ait-aecid/aecid-parsergenerator)
Automatically create parser trees for textual logdata to facilitate analysis.

Please install python-dateutil before continuing. The aecid-parsergenerator was tested with python-dateutil 2.8.1, but should work with other versions as well.
```
pip3 install python-dateutil
```

To get started, just clone this repository and execute
```
python3 AECIDpg.py
```
to run the aecid-parsergenerator with the default input file and configurations. To change the configuration, edit the PGConfig.py file.

There are two sample configurations for Exim Mainlog and Audit logs. Just copy either of the configurations by
```
cp configs/PGConfig_mainlog.py PGConfig.py
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
or open data/out/visualization.png (note that visualization requires `sudo apt-get install -y python3-pygraphviz` and `pip install pygraphviz`, and needs to be activated by setting `visualize = True` in the configuration).

More information on the aecid-parsergenerator is provided in the following paper: 

Wurzenberger M., Landauer M., Skopik F., Kastner W. (2019): [AECID-PG: A Tree-Based Log Parser Generator To Enable Log Analysis](https://ieeexplore.ieee.org/document/8717887). [4th IEEE/IFIP International Workshop on Analytics for Network and Service Management (AnNet 2019)](https://annet2019.moogsoft.com/) in conjunction with the [IFIP/IEEE International Symposium on Integrated Network Management (IM)](https://im2019.ieee-im.org/), April 8, 2019, Washington D.C., USA. IEEE. \[[PDF](https://www.markuswurzenberger.com/wp-content/uploads/2020/05/2019_annet.pdf)\]
