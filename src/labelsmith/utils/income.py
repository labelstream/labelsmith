# noinspection SpellCheckingInspection
def simulate(
    hours: int | float = None,
    payrate: int | float = 18.00,
    taxrate: int | float = 0.27,
    gross: int | float = None,
    net: int | float = None,
) -> None:
    """
    Simulate income.

    NOTE: Only certain combinations work right now;
    development is working to make this function more robust.

    :param hours: int | float
    :param payrate: int | float
    :param taxrate: int | float
    :param gross: int | float
    :param net: int | float
    :return: str
    """
    try:
        if hours is not None and payrate is not None:
            gross = round(hours * payrate, 2)
            tax = round(gross * taxrate, 2)
            net = round(gross - tax, 2)
            print(f"""
            
If you worked {hours:.2f} hours at ${payrate:.2f}/hr, 
then you earned ${gross:.2f} in gross income.
>  At a rate of {taxrate:.2f}, your tax liability is ${tax:.2f}.
>  Your net income, then, is ${net:.2f}.
              
"""
                  )
        elif gross is not None and payrate is not None:
            hours = round(gross / payrate, 2)
            tax = round(gross * taxrate, 2)
            net = round(gross - tax, 2)
            print(f"""
            
To yield ${gross:.2f} in gross income at $
{payrate:.2f}/hr, you would need to work {hours:.2f} hours.
>  At a rate of {taxrate:.2f}, your tax liability would be ${tax:.2f}.
>  Your net income would then be ${net:.2f}.
              
"""
                  )

        elif net is not None and payrate is not None:
            gross = round(net / (1 - taxrate), 2)
            hours = round(gross / payrate, 2)
            tax = round(gross * taxrate, 2)
            print(f"""
            
To yield ${net:.2f} in net income at ${payrate:.2f}/hr, 
you would need to work {hours:.2f} hours.
>  This corresponds to ${gross:.2f} in gross income. 
>  At a rate of {taxrate:.2f}, your tax liability would be ${tax:.2f}.
            
"""
                  )

        elif gross is not None and net is not None and taxrate is None:
            taxrate = round(1 - (net / gross), 4)
            hours = round(gross / payrate, 2)
            print(f"""
            
If you grossed ${gross:.2f} and netted ${net:.2f}, then you worked
 {hours:.2f} hours and were taxed at a rate of {taxrate:.2f}.

"""
                  )
        else:
            print("""

Error: Provide hours+payrate, gross+payrate, net+payrate, 
or gross+net.

"""
                  )

    except Exception as e:
        print(f"Error: {e}")
    return
