"""
api:
    call heuristic(totals)

    where totals is a dict person -> credit.
    For instance: {<object1>: 5, <object2>: -3, <object3>: -2}

    you'll get a collection of transfer instructions, like:
        giver, receiver, value

Requisite:
    Totals must be balanced.

    Maybe evolution: drop this requisite and provide a NOBODY person,
    that will be used to balance the last debt/lend, leaving it up to the
    caller to assert there is no expected transfert to/from NOBODY, or that
    such a transfer is not exceeding a certain value.

How it works:
    While lends and debs, loop on the following:
        If exact matches are found, they are returned.
        Bigger values are then matched against each other such as to
        solve the 'problem' for one person at least.
"""

from decimal import Decimal, getcontext, ROUND_FLOOR

getcontext().rounding=ROUND_FLOOR

DEC_O = Decimal(0)
PRECISION = Decimal("0.0000001")


def _exactmmatch(personstotals, total):
    """
    personstotals is expected as a list of (person, credit)
    The sign of credit is opposite to the sign of total and person
    is not contained in personstotals
    """
    for otherperson, othertotal in personstotals:
        if othertotal.quantize(PRECISION) != - total.quantize(PRECISION):
            continue
        return otherperson

def _reverseabsvalue(item, otheritem):
    """
    item, otheritem is expected as (*, number, ****)
    """
    return cmp(abs(otheritem[1]), abs(item[1]))


def heuristic(totals):
    """
    totals is expected as a dict: {person, credit}
    """
    #initialization
    debts = [
        [person, value]
        for person, value in totals.iteritems()
        if value < DEC_O
    ]
    lends = [
        [person, value]
        for person, value in totals.iteritems()
        if value > DEC_O
    ]
    result = [
        (person, None, DEC_O)
        for person, value in totals.iteritems()
        if value == DEC_O
    ]
    #loop
    while lends or debts:
        #1st step: exact matches
        #iter on a copy of lends
        for person, value in tuple(lends):
            match = _exactmmatch(debts, value)
            if match:
                result.append((match, person, value))
                lends.remove(
                    [person, value]
                )
                debts.remove(
                    [match, - value]
                )
        #continue to 2nd step?
        if not lends and not debts:
            break
        if bool(lends) != bool(debts):
            assert False, "Lends: %s, debts: %s" % (lends, debts)
        #prepare 2nd step
        debts.sort(_reverseabsvalue)
        lends.sort(_reverseabsvalue)
        #2nd step: make the biggest possible transfer
        biggestdebt = debts[0][1]
        biggestcredit = lends[0][1]
        transfer = min( - biggestdebt, biggestcredit)
        result.append((debts[0][0], lends[0][0], transfer))
        debts[0][1] += transfer
        lends[0][1] -= transfer
        #purge
        for collection in (lends, debts):
            for item in tuple(collection):
                if item[1] == DEC_O:
                    collection.remove(item)

    return result
