

Bravo! You have received a Mercantilism Diploma in "rollercoaster" from the Orbital Convergence University International Air and Water Embassy of the Tangerine Planet (the planet that is one ellipse further from the Sun than Earth's ellipse).

You are now officially certified to include "rollercoaster" in your practice.

--
# rollercoaster

## install
```
pip install rollercoaster
```

## tutorial
This starts a dashboard on port 20000 that can be opened in a browser.
```
rollercoaster help
```
```
rollercoaster help --port 20001
```


## rides (OCHLV)
rides.season_3.super_hero_trend

## stats (options)
### stats.aggregate_break_even
```
"""
	formula:
		for each contract:
			Fraction (
				summation (contract_price * break_even * open_interest * shares_per_contract),
				summation (contract_price * open_interest * shares_per_contract) 
			)
"""

Tradier_API_authorization = ""
		
#
#	This presumes that the symbol is unique...
#
import rollercoaster.clouds.Tradier.procedures.options.combine as combine_options  
import rollercoaster.stats.aggregate_break_even as aggregate_break_even
break_evens = aggregate_break_even.calc ({
	"expirations": combine_options.presently ({
		"symbol": "SOYB",
		"authorization": Tradier_API_authorization
	})
})

import rich
rich.print_json (data = break_evens)

```

### stats.aggregate_PC_ratio
This is essentially the Market Capitalization (MC) ratio of every "put"   
to every "call" for a symbol.   

```
	example:
		2 : 1

		indicates that:
			2/3 of the money is on puts 
			1/3 of the money is on calls
```


```
	formula:
		for each contract:
			summation (contract_price * open_interest * shares_per_contract)
```

```
import rollercoaster.stats.aggregate_PC_ratio as aggregate_PC_ratio
import rollercoaster.clouds.Tradier.procedures.options.combine as combine_options  
PC_ratios = aggregate_PC_ratio.calc ({
	"expirations": combine_options.presently ({
		"symbol": "SOYB",
		"authorization": Tradier_API_authorization
	})
})

import rich
rich.print_json (data = {
	"PC ratios": PC_ratios
})
```


## clouds
clouds.Coinbase.API.products.candles
