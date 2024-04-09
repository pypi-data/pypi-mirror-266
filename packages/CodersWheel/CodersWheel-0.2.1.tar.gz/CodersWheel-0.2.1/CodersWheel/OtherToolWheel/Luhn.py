# coding=utf8

class Luhn(object):
    @staticmethod
    def digits_of(n):
        return [int(d) for d in str(n)]

    @classmethod
    def createcode(cls, number):
        lastdigit = cls.luhn_checksum(number)
        return int("{}{}".format(str(number), str(lastdigit)))

    @classmethod
    def luhn_checksum(cls, codenumber):
        digits = cls.digits_of(codenumber)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(cls.digits_of(d * 2))
        return checksum % 10

    @classmethod
    def is_luhn_valid(cls, code_number):
        return cls.luhn_checksum(code_number) == 0


if __name__ == '__main__':
    print(Luhn.createcode(1234567890))
    print(Luhn.is_luhn_valid(12345678902))

