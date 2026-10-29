#!/usr/bin/env python3
"""Apply one named source variant to work2/ws from work2/pristine. usage: apply_variant.py <name>"""
import sys
from pathlib import Path
W = Path("/mnt/c/Users/arzfeqsdeidm/Desktop/yop/AA/work-pump/packet-maintained/work2")
rel = "programs/pump/src/buy.rs"
base = (W / "pristine" / rel).read_text()
lines = base.splitlines(keepends=True)

def setline(i, text):
    # i is 1-based; keep the original line terminator
    old = lines[i - 1]
    term = "\r\n" if old.endswith("\r\n") else "\n"
    lines[i - 1] = text + term

name = sys.argv[1]
if name == "v1":          # line 110: explicit zero test
    setline(110, " if quote==0{return Err(PumpError::BuySlippageBelowMinTokensOut.into());}")
elif name == "v2":        # line 92: explicit zero test
    setline(92, " if raw_quote==0{return Err(PumpError::BuyNotEnoughSolToCoverFees.into());}")
elif name == "v3":        # both 92 and 110
    setline(92, " if raw_quote==0{return Err(PumpError::BuyNotEnoughSolToCoverFees.into());}")
    setline(110, " if quote==0{return Err(PumpError::BuySlippageBelowMinTokensOut.into());}")
elif name == "v1c":       # line 110: faithful inversion, keeps error!+with_values
    setline(110, " if quote>0{}else{return Err(error!(PumpError::BuySlippageBelowMinTokensOut).with_values((quote,0)));}")
elif name == "v1d":       # line 110: explicit zero test with error!+with_values
    setline(110, " if quote==0{return Err(error!(PumpError::BuySlippageBelowMinTokensOut).with_values((quote,0)));}")
elif name == "v2c":       # line 92: faithful inversion
    setline(92, " if raw_quote>0{}else{return Err(error!(PumpError::BuyNotEnoughSolToCoverFees).with_values((raw_quote,0)));}")
elif name == "v3c":       # lines 92 + 110: faithful inversions
    setline(92, " if raw_quote>0{}else{return Err(error!(PumpError::BuyNotEnoughSolToCoverFees).with_values((raw_quote,0)));}")
    setline(110, " if quote>0{}else{return Err(error!(PumpError::BuySlippageBelowMinTokensOut).with_values((quote,0)));}")
elif name == "a1":       # function attribute: inline(never)
    setline(9, lines[8].rstrip("\r\n").replace("#[inline]", "#[inline(never)]"))
elif name == "a2":       # function attribute: cold + inline(never)
    setline(9, lines[8].rstrip("\r\n").replace("#[inline]", "#[cold] #[inline(never)]"))
elif name == "a3":       # function attribute: none
    setline(9, lines[8].rstrip("\r\n").replace("#[inline] ", ""))
elif name == "a4":       # function attribute: inline(always)
    setline(9, lines[8].rstrip("\r\n").replace("#[inline]", "#[inline(always)]"))
elif name in ("e1", "e2", "e3"):
    helper = ("#[cold] #[inline(never)]" if name != "e2" else "#[inline(always)]") + \
             " fn pump_cold_error(e:anchor_lang::error::Error)->anchor_lang::error::Error{e}\n"
    if name in ("e1", "e3"):
        setline(110, " if quote==0{return Err(pump_cold_error(error!(PumpError::BuySlippageBelowMinTokensOut).with_values((quote,0))));}")
    if name == "e3":
        setline(92, " if raw_quote==0{return Err(pump_cold_error(error!(PumpError::BuyNotEnoughSolToCoverFees).with_values((raw_quote,0))));}")
    lines.append(helper)
elif name == "v4":        # line 57 + 59 explicit zero tests
    setline(57, " if min_tokens_out==0{return Err(PumpError::BuyZeroAmount.into());}")
    setline(59, " if spendable_sol_in==0{return Err(PumpError::BuyNotEnoughSolToCoverFees.into());}")
elif name == "v5":        # all four zero tests explicit
    setline(57, " if min_tokens_out==0{return Err(PumpError::BuyZeroAmount.into());}")
    setline(59, " if spendable_sol_in==0{return Err(PumpError::BuyNotEnoughSolToCoverFees.into());}")
    setline(92, " if raw_quote==0{return Err(PumpError::BuyNotEnoughSolToCoverFees.into());}")
    setline(110, " if quote==0{return Err(PumpError::BuySlippageBelowMinTokensOut.into());}")
else:
    raise SystemExit("unknown variant " + name)
out = "".join(lines)
dst = W / "ws" / rel
dst.write_text(out)
# record exact diff
import difflib
diff = list(difflib.unified_diff(base.splitlines(), out.splitlines(), "pristine", name, lineterm="", n=1))
(W / ("diff-" + name + ".patch")).write_text("\n".join(diff) + "\n")
print("\n".join(diff))
