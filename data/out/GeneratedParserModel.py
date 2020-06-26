"""This module defines a generated parser model."""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import AnyMatchModelElement
from aminer.parsing import Base64StringModelElement
from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalFloatValueModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import HexStringModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import OptionalMatchModelElement
from aminer.parsing import SequenceModelElement
from aminer.parsing import VariableByteDataModelElement

def get_model():
	alphabet = b'!"#$%&\'()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'


	model = SequenceModelElement('sequence1', [
		FixedDataModelElement('fixed2', b'type='),
		FirstMatchModelElement('firstmatch3', [
			SequenceModelElement('sequence4', [
				FixedDataModelElement('fixed5', b'PROCTITLE msg='),
				VariableByteDataModelElement('string6', alphabet),
				FixedDataModelElement('fixed7', b' proctitle='),
				FirstMatchModelElement('firstmatch8', [
					FixedDataModelElement('fixed9', b'2F7573722F7362696E2F61706163686532002D6B007374617274'),
					VariableByteDataModelElement('string10', alphabet)])]),
			SequenceModelElement('sequence11', [
				FixedDataModelElement('fixed12', b'SYSCALL msg='),
				VariableByteDataModelElement('string13', alphabet),
				FixedDataModelElement('fixed14', b' arch=c000003e syscall='),
				DecimalIntegerValueModelElement('integer15', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed16', b' success='),
				FirstMatchModelElement('firstmatch17', [
					SequenceModelElement('sequence18', [
						FixedDataModelElement('fixed19', b'yes exit='),
						DecimalIntegerValueModelElement('integer20', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed21', b' a0='),
						VariableByteDataModelElement('string22', alphabet),
						FixedDataModelElement('fixed23', b' a1='),
						VariableByteDataModelElement('string24', alphabet),
						FixedDataModelElement('fixed25', b' a2='),
						VariableByteDataModelElement('string26', alphabet),
						FixedDataModelElement('fixed27', b' a3='),
						VariableByteDataModelElement('string28', alphabet),
						FixedDataModelElement('fixed29', b' items='),
						DecimalIntegerValueModelElement('integer30', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed31', b' ppid='),
						DecimalIntegerValueModelElement('integer32', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed33', b' pid='),
						DecimalIntegerValueModelElement('integer34', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed35', b' auid='),
						DecimalIntegerValueModelElement('integer36', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed37', b' uid='),
						DecimalIntegerValueModelElement('integer38', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed39', b' gid='),
						DecimalIntegerValueModelElement('integer40', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed41', b' euid='),
						DecimalIntegerValueModelElement('integer42', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed43', b' suid='),
						DecimalIntegerValueModelElement('integer44', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed45', b' fsuid='),
						DecimalIntegerValueModelElement('integer46', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed47', b' egid='),
						DecimalIntegerValueModelElement('integer48', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed49', b' sgid='),
						DecimalIntegerValueModelElement('integer50', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed51', b' fsgid='),
						DecimalIntegerValueModelElement('integer52', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed53', b' tty=(none) ses='),
						DecimalIntegerValueModelElement('integer54', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed55', b' comm='),
						FirstMatchModelElement('firstmatch56', [
							FixedDataModelElement('fixed57', b'"apache2" exe="/usr/sbin/apache2" key=(null)'),
							SequenceModelElement('sequence58', [
								VariableByteDataModelElement('string59', alphabet),
								FixedDataModelElement('fixed60', b' exe='),
								FirstMatchModelElement('firstmatch61', [
									FixedDataModelElement('fixed62', b'"/usr/bin/suricata" key=(null)'),
									SequenceModelElement('sequence63', [
										VariableByteDataModelElement('string64', alphabet),
										FixedDataModelElement('fixed65', b' key=(null)')])])])])]),
					SequenceModelElement('sequence66', [
						VariableByteDataModelElement('string67', alphabet),
						FixedDataModelElement('fixed68', b' exit='),
						DecimalIntegerValueModelElement('integer69', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed70', b' a0='),
						VariableByteDataModelElement('string71', alphabet),
						FixedDataModelElement('fixed72', b' a1='),
						VariableByteDataModelElement('string73', alphabet),
						FixedDataModelElement('fixed74', b' a2='),
						VariableByteDataModelElement('string75', alphabet),
						FixedDataModelElement('fixed76', b' a3='),
						VariableByteDataModelElement('string77', alphabet),
						FixedDataModelElement('fixed78', b' items='),
						DecimalIntegerValueModelElement('integer79', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed80', b' ppid='),
						DecimalIntegerValueModelElement('integer81', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed82', b' pid='),
						DecimalIntegerValueModelElement('integer83', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed84', b' auid='),
						DecimalIntegerValueModelElement('integer85', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed86', b' uid='),
						DecimalIntegerValueModelElement('integer87', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed88', b' gid='),
						DecimalIntegerValueModelElement('integer89', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed90', b' euid='),
						DecimalIntegerValueModelElement('integer91', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed92', b' suid='),
						DecimalIntegerValueModelElement('integer93', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed94', b' fsuid='),
						DecimalIntegerValueModelElement('integer95', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed96', b' egid='),
						DecimalIntegerValueModelElement('integer97', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed98', b' sgid='),
						DecimalIntegerValueModelElement('integer99', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed100', b' fsgid='),
						DecimalIntegerValueModelElement('integer101', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed102', b' tty=(none) ses='),
						DecimalIntegerValueModelElement('integer103', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed104', b' comm="apache2" exe="/usr/sbin/apache2" key=(null)')])])]),
			SequenceModelElement('sequence105', [
				FixedDataModelElement('fixed106', b'PATH msg='),
				VariableByteDataModelElement('string107', alphabet),
				FixedDataModelElement('fixed108', b' item='),
				DecimalIntegerValueModelElement('integer109', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed110', b' name='),
				VariableByteDataModelElement('string111', alphabet),
				FixedDataModelElement('fixed112', b' '),
				FirstMatchModelElement('firstmatch113', [
					SequenceModelElement('sequence114', [
						FixedDataModelElement('fixed115', b'inode='),
						DecimalIntegerValueModelElement('integer116', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed117', b' dev='),
						FirstMatchModelElement('firstmatch118', [
							SequenceModelElement('sequence119', [
								FixedDataModelElement('fixed120', b'fe:01 mode='),
								DecimalIntegerValueModelElement('integer121', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed122', b' ouid='),
								DecimalIntegerValueModelElement('integer123', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed124', b' ogid='),
								DecimalIntegerValueModelElement('integer125', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed126', b' rdev=00:00 nametype='),
								FirstMatchModelElement('firstmatch127', [
									FixedDataModelElement('fixed128', b'NORMAL'),
									VariableByteDataModelElement('string129', alphabet)])]),
							SequenceModelElement('sequence130', [
								VariableByteDataModelElement('string131', alphabet),
								FixedDataModelElement('fixed132', b' mode='),
								DecimalIntegerValueModelElement('integer133', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed134', b' ouid='),
								DecimalIntegerValueModelElement('integer135', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed136', b' ogid='),
								DecimalIntegerValueModelElement('integer137', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed138', b' rdev=00:00 nametype=NORMAL')])])]),
					SequenceModelElement('sequence139', [
						VariableByteDataModelElement('string140', alphabet),
						FixedDataModelElement('fixed141', b'=UNKNOWN')])])]),
			SequenceModelElement('sequence142', [
				VariableByteDataModelElement('string143', alphabet),
				FixedDataModelElement('fixed144', b' msg='),
				VariableByteDataModelElement('string145', alphabet),
				FixedDataModelElement('fixed146', b' saddr='),
				FixedWordlistDataModelElement('fixed147', [b'01002F7661722F72756E2F6D7973716C642F6D7973716C642E736F636B', b'020000350A12FFFE0000000000000000'])])])])

	return model