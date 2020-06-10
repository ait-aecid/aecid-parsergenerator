"""This module defines a generated parser model."""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import AnyMatchModelElement
from aminer.parsing import Base64StringModelElement
from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalFloatValueModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
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

	sub_tree0 = SequenceModelElement('sequence0', [
		FixedDataModelElement('fixed1', b' key=(null)')])

	sub_tree1 = SequenceModelElement('sequence1', [
		FixedDataModelElement('fixed2', b'"apache2" exe="/usr/sbin/apache2" key=(null)')])


	model = SequenceModelElement('sequence3', [
		FixedDataModelElement('fixed4', b'type='),
		FirstMatchModelElement('firstmatch5', [
			SequenceModelElement('sequence6', [
				FixedDataModelElement('fixed7', b'PROCTITLE msg='),
				VariableByteDataModelElement('string8', alphabet),
				FixedDataModelElement('fixed9', b' proctitle='),
				FirstMatchModelElement('firstmatch10', [
					FixedDataModelElement('fixed11', b'2F7573722F7362696E2F61706163686532002D6B007374617274'),
					VariableByteDataModelElement('string12', alphabet)])]),
			SequenceModelElement('sequence13', [
				FixedDataModelElement('fixed14', b'SYSCALL msg='),
				VariableByteDataModelElement('string15', alphabet),
				FixedDataModelElement('fixed16', b' arch=c000003e syscall='),
				DecimalIntegerValueModelElement('integer17', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed18', b' success='),
				FirstMatchModelElement('firstmatch19', [
					SequenceModelElement('sequence20', [
						FixedDataModelElement('fixed21', b'yes exit='),
						DecimalIntegerValueModelElement('integer22', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed23', b' a0='),
						VariableByteDataModelElement('string24', alphabet),
						FixedDataModelElement('fixed25', b' a1='),
						VariableByteDataModelElement('string26', alphabet),
						FixedDataModelElement('fixed27', b' a2='),
						VariableByteDataModelElement('string28', alphabet),
						FixedDataModelElement('fixed29', b' a3='),
						VariableByteDataModelElement('string30', alphabet),
						FixedDataModelElement('fixed31', b' items='),
						DecimalIntegerValueModelElement('integer32', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed33', b' ppid='),
						DecimalIntegerValueModelElement('integer34', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed35', b' pid='),
						DecimalIntegerValueModelElement('integer36', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed37', b' auid='),
						DecimalIntegerValueModelElement('integer38', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed39', b' uid='),
						DecimalIntegerValueModelElement('integer40', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed41', b' gid='),
						DecimalIntegerValueModelElement('integer42', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed43', b' euid='),
						DecimalIntegerValueModelElement('integer44', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed45', b' suid='),
						DecimalIntegerValueModelElement('integer46', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed47', b' fsuid='),
						DecimalIntegerValueModelElement('integer48', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed49', b' egid='),
						DecimalIntegerValueModelElement('integer50', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed51', b' sgid='),
						DecimalIntegerValueModelElement('integer52', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed53', b' fsgid='),
						DecimalIntegerValueModelElement('integer54', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed55', b' tty=(none) ses='),
						DecimalIntegerValueModelElement('integer56', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed57', b' comm='),
						FirstMatchModelElement('firstmatch58', [
							sub_tree1,
							SequenceModelElement('sequence59', [
								VariableByteDataModelElement('string60', alphabet),
								FixedDataModelElement('fixed61', b' exe='),
								FirstMatchModelElement('firstmatch62', [
									SequenceModelElement('sequence63', [
										FixedDataModelElement('fixed64', b'"/usr/bin/suricata"'),
										sub_tree0]),
									SequenceModelElement('sequence65', [
										VariableByteDataModelElement('string66', alphabet),
										sub_tree0])])])])]),
					SequenceModelElement('sequence67', [
						VariableByteDataModelElement('string68', alphabet),
						FixedDataModelElement('fixed69', b' exit='),
						DecimalIntegerValueModelElement('integer70', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed71', b' a0='),
						VariableByteDataModelElement('string72', alphabet),
						FixedDataModelElement('fixed73', b' a1='),
						VariableByteDataModelElement('string74', alphabet),
						FixedDataModelElement('fixed75', b' a2='),
						VariableByteDataModelElement('string76', alphabet),
						FixedDataModelElement('fixed77', b' a3='),
						VariableByteDataModelElement('string78', alphabet),
						FixedDataModelElement('fixed79', b' items='),
						DecimalIntegerValueModelElement('integer80', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed81', b' ppid='),
						DecimalIntegerValueModelElement('integer82', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed83', b' pid='),
						DecimalIntegerValueModelElement('integer84', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed85', b' auid='),
						DecimalIntegerValueModelElement('integer86', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed87', b' uid='),
						DecimalIntegerValueModelElement('integer88', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed89', b' gid='),
						DecimalIntegerValueModelElement('integer90', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed91', b' euid='),
						DecimalIntegerValueModelElement('integer92', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed93', b' suid='),
						DecimalIntegerValueModelElement('integer94', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed95', b' fsuid='),
						DecimalIntegerValueModelElement('integer96', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed97', b' egid='),
						DecimalIntegerValueModelElement('integer98', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed99', b' sgid='),
						DecimalIntegerValueModelElement('integer100', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed101', b' fsgid='),
						DecimalIntegerValueModelElement('integer102', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed103', b' tty=(none) ses='),
						DecimalIntegerValueModelElement('integer104', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed105', b' comm='),
						sub_tree1])])]),
			SequenceModelElement('sequence106', [
				FixedDataModelElement('fixed107', b'PATH msg='),
				VariableByteDataModelElement('string108', alphabet),
				FixedDataModelElement('fixed109', b' item='),
				DecimalIntegerValueModelElement('integer110', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed111', b' name='),
				VariableByteDataModelElement('string112', alphabet),
				FixedDataModelElement('fixed113', b' '),
				FirstMatchModelElement('firstmatch114', [
					SequenceModelElement('sequence115', [
						FixedDataModelElement('fixed116', b'inode='),
						DecimalIntegerValueModelElement('integer117', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed118', b' dev='),
						FirstMatchModelElement('firstmatch119', [
							SequenceModelElement('sequence120', [
								FixedDataModelElement('fixed121', b'fe:01 mode='),
								DecimalIntegerValueModelElement('integer122', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed123', b' ouid='),
								DecimalIntegerValueModelElement('integer124', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed125', b' ogid='),
								DecimalIntegerValueModelElement('integer126', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed127', b' rdev=00:00 nametype='),
								FirstMatchModelElement('firstmatch128', [
									FixedDataModelElement('fixed129', b'NORMAL'),
									VariableByteDataModelElement('string130', alphabet)])]),
							SequenceModelElement('sequence131', [
								VariableByteDataModelElement('string132', alphabet),
								FixedDataModelElement('fixed133', b' mode='),
								DecimalIntegerValueModelElement('integer134', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed135', b' ouid='),
								DecimalIntegerValueModelElement('integer136', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed137', b' ogid='),
								DecimalIntegerValueModelElement('integer138', value_sign_type = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
								FixedDataModelElement('fixed139', b' rdev=00:00 nametype=NORMAL')])])]),
					SequenceModelElement('sequence140', [
						VariableByteDataModelElement('string141', alphabet),
						FixedDataModelElement('fixed142', b'=UNKNOWN')])])]),
			SequenceModelElement('sequence143', [
				VariableByteDataModelElement('string144', alphabet),
				FixedDataModelElement('fixed145', b' msg='),
				VariableByteDataModelElement('string146', alphabet),
				FixedDataModelElement('fixed147', b' saddr='),
				FixedWordlistDataModelElement('fixed148', [b'01002F7661722F72756E2F6D7973716C642F6D7973716C642E736F636B', b'020000350A12FFFE0000000000000000'])])])])

	return model