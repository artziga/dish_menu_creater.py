def score(dice):
    result = 0
    d = {num: dice.count(num) for num in dice}
    for key in d:
        whole = d[key] // 3
        rest = d[key] % 3
        if key == 5:
            result += rest * 50 + whole * key * 100
        elif key == 1:
            result += rest * 100 + whole * key * 1000
        else:
            result += whole * key * 100

    return result


print(score([4, 4, 4, 3, 3]))