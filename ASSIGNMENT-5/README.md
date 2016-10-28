1. Selective repeat:

go into the directory Selective_repeat:
$cd Selective_repeat

open a new tab.

First run the receiver in one of the tabs:
$python B.py <loss_p> <corrupt_p> <trace>

Then run the sender in the other tab:
$python A.py <n> <time> <trace>

2. Go-back-n:

go into the directory Go_back_n
$cd Go_back_n

follow the same steps as that for selective repeat.


Index:

<loss_p>: loss probability (0 - 1)
<corrupt_p>: corruption probability (0-1)
<trace>: 0 for no debugging info, 1 for all information
<n>: number of packets to be sent by sender
<time>: The time_out for the acknowledgment to be received.