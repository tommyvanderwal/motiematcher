# CRITICAL DISCOVERY: Parliament Member Collection Issue

## Problem Identified
Our current collection logic uses the `/Persoon` endpoint, which returns 221 persons with all fields set to `null`. This is because the basic `Persoon` endpoint only contains structural person data without parliamentary functions.

## Root Cause
The Dutch Parliament API separates person data from parliamentary functions:
- `/Persoon` = Basic person records (mostly empty/null)
- `/FractieZetelPersoon` = Links between persons and parliamentary seats

## Solution Found
Use `/FractieZetelPersoon` endpoint with date filtering to get active parliament members:

```odata
/FractieZetelPersoon?$filter=Van le 2023-12-06T00:00:00Z and (TotEnMet eq null or TotEnMet gt 2023-12-06T00:00:00Z)
```

This returns exactly **150 active parliament members** for the current parliament period.

## Key Findings
- ✅ **FractieZetelPersoon API**: Returns 150 active members
- ✅ **Unique persons**: 150 (matches expectation)
- ✅ **Active criteria**: `TotEnMet eq null`
- ✅ **Parliament start**: December 6, 2023
- ❌ **Persoon API**: Returns empty/null data

## Required Fix
Modify collection logic to:
1. Query `FractieZetelPersoon` for active members
2. Extract `Persoon_Id` values
3. Query `Persoon` endpoint for those specific IDs
4. This will give us complete person data for the 150 active parliament members

## Impact
- **Before**: 221 persons with unknown status, 0 active members found
- **After**: 150 persons with complete data, all active parliament members

## Next Steps
1. Update `full_term_collector.py` to use `FractieZetelPersoon` approach
2. Test collection of person details for the 150 active members
3. Validate data completeness and accuracy