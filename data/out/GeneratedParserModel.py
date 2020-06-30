"""This module defines a generated parser model."""

from aminer.parsing import AnyByteDataModelElement
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
	alphabet = b'!"#$%&\'*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
	model = SequenceModelElement('sequence0', [
		FixedDataModelElement('fixed1', b'type='),
		FirstMatchModelElement('firstmatch2', [
			SequenceModelElement('sequence3', [
				FixedDataModelElement('fixed4', b'USER_AUTH msg=audit('),
				VariableByteDataModelElement('string5', alphabet),
				FixedDataModelElement('fixed6', b'): pid='),
				DecimalIntegerValueModelElement('integer7', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed8', b' uid='),
				DecimalIntegerValueModelElement('integer9', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed10', b' auid='),
				DecimalIntegerValueModelElement('integer11', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed12', b' ses='),
				DecimalIntegerValueModelElement('integer13', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed14', b' msg=\'op=PAM:authentication acct='),
				VariableByteDataModelElement('string15', alphabet),
				FixedDataModelElement('fixed16', b' exe="/usr/lib/dovecot/auth" hostname='),
				IpAddressDataModelElement('ipaddress17'),
				FixedDataModelElement('fixed18', b' addr='),
				IpAddressDataModelElement('ipaddress19'),
				FixedDataModelElement('fixed20', b' terminal=dovecot res=success\'')]),
			SequenceModelElement('sequence21', [
				FixedDataModelElement('fixed22', b'USER_ACCT msg=audit('),
				VariableByteDataModelElement('string23', alphabet),
				FixedDataModelElement('fixed24', b'): pid='),
				DecimalIntegerValueModelElement('integer25', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed26', b' uid='),
				DecimalIntegerValueModelElement('integer27', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed28', b' auid='),
				DecimalIntegerValueModelElement('integer29', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed30', b' ses='),
				DecimalIntegerValueModelElement('integer31', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed32', b' msg=\'op=PAM:accounting acct='),
				VariableByteDataModelElement('string33', alphabet),
				FixedDataModelElement('fixed34', b' exe="/usr/lib/dovecot/auth" hostname='),
				IpAddressDataModelElement('ipaddress35'),
				FixedDataModelElement('fixed36', b' addr='),
				IpAddressDataModelElement('ipaddress37'),
				FixedDataModelElement('fixed38', b' terminal=dovecot res=success\'')]),
			SequenceModelElement('sequence39', [
				FixedDataModelElement('fixed40', b'PROCTITLE msg=audit('),
				VariableByteDataModelElement('string41', alphabet),
				FixedDataModelElement('fixed42', b'): proctitle='),
				VariableByteDataModelElement('string43', alphabet)]),
			SequenceModelElement('sequence44', [
				FixedDataModelElement('fixed45', b'SOCKADDR msg=audit('),
				VariableByteDataModelElement('string46', alphabet),
				FixedDataModelElement('fixed47', b'): saddr='),
				VariableByteDataModelElement('string48', alphabet)]),
			SequenceModelElement('sequence49', [
				FixedDataModelElement('fixed50', b'SYSCALL msg=audit('),
				VariableByteDataModelElement('string51', alphabet),
				FixedDataModelElement('fixed52', b'): arch=c000003e syscall='),
				DecimalIntegerValueModelElement('integer53', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed54', b' success='),
				VariableByteDataModelElement('string55', alphabet),
				FixedDataModelElement('fixed56', b' exit='),
				DecimalIntegerValueModelElement('integer57', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed58', b' a0='),
				VariableByteDataModelElement('string59', alphabet),
				FixedDataModelElement('fixed60', b' a1='),
				VariableByteDataModelElement('string61', alphabet),
				FixedDataModelElement('fixed62', b' a2='),
				VariableByteDataModelElement('string63', alphabet),
				FixedDataModelElement('fixed64', b' a3='),
				VariableByteDataModelElement('string65', alphabet),
				FixedDataModelElement('fixed66', b' items='),
				DecimalIntegerValueModelElement('integer67', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed68', b' ppid='),
				DecimalIntegerValueModelElement('integer69', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed70', b' pid='),
				DecimalIntegerValueModelElement('integer71', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed72', b' auid='),
				DecimalIntegerValueModelElement('integer73', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed74', b' uid='),
				DecimalIntegerValueModelElement('integer75', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed76', b' gid='),
				DecimalIntegerValueModelElement('integer77', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed78', b' euid='),
				DecimalIntegerValueModelElement('integer79', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed80', b' suid='),
				DecimalIntegerValueModelElement('integer81', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed82', b' fsuid='),
				DecimalIntegerValueModelElement('integer83', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed84', b' egid='),
				DecimalIntegerValueModelElement('integer85', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed86', b' sgid='),
				DecimalIntegerValueModelElement('integer87', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed88', b' fsgid='),
				DecimalIntegerValueModelElement('integer89', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed90', b' tty=(none) ses='),
				DecimalIntegerValueModelElement('integer91', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed92', b' comm='),
				VariableByteDataModelElement('string93', alphabet),
				FixedDataModelElement('fixed94', b' exe='),
				VariableByteDataModelElement('string95', alphabet),
				FixedDataModelElement('fixed96', b' key=(null)')]),
			SequenceModelElement('sequence97', [
				FixedDataModelElement('fixed98', b'EXECVE msg=audit('),
				VariableByteDataModelElement('string99', alphabet),
				FixedDataModelElement('fixed100', b'): argc='),
				DecimalIntegerValueModelElement('integer101', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed102', b' a0='),
				VariableByteDataModelElement('string103', alphabet),
				OptionalMatchModelElement('optional104', 
					SequenceModelElement('sequence105', [
						FixedDataModelElement('fixed106', b' a1="-w"')]))]),
			SequenceModelElement('sequence107', [
				FixedDataModelElement('fixed108', b'PATH msg=audit('),
				VariableByteDataModelElement('string109', alphabet),
				FixedDataModelElement('fixed110', b'): item='),
				DecimalIntegerValueModelElement('integer111', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
				FixedDataModelElement('fixed112', b' name='),
				VariableByteDataModelElement('string113', alphabet),
				FixedDataModelElement('fixed114', b' '),
				VariableByteDataModelElement('string115', alphabet),
				FixedDataModelElement('fixed116', b'='),
				VariableByteDataModelElement('string117', alphabet),
				OptionalMatchModelElement('optional118', 
					SequenceModelElement('sequence119', [
						FixedDataModelElement('fixed120', b' dev='),
						VariableByteDataModelElement('string121', alphabet),
						FixedDataModelElement('fixed122', b' mode='),
						DecimalIntegerValueModelElement('integer123', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed124', b' ouid='),
						DecimalIntegerValueModelElement('integer125', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed126', b' ogid='),
						DecimalIntegerValueModelElement('integer127', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),
						FixedDataModelElement('fixed128', b' rdev='),
						VariableByteDataModelElement('string129', alphabet),
						FixedDataModelElement('fixed130', b' nametype='),
						VariableByteDataModelElement('string131', alphabet)]))])])])

	return model