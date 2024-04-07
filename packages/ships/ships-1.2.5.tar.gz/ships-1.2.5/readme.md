


******

Bravo!  You have received a Medical Diploma in Ships from   
the Orbital Convergence University International Air and Water Embassy of the Tangerine Planet.  

You are now officially certified to include "ships" in your practice.

******


# ships

---

## description
This is a kit of python3 modules.
		
---		
		
## install
`[ZSH] pip install ships`



## check equality
```
[xonsh] ships check-equality --dir-1 {dir 1} --dir-2 {dir 2}
```

## find and replace a string

Make sure the git repository doesn't have any changes before   
running this, in the event that there is a problem.  

Itinerary: add "exclude_paths".   
    
Caution: Make sure there aren't any image or video files in the path.   
   
```
import ships.paths.directory.find_and_replace_string_v2 as find_and_replace_string_v2

import pathlib
from os.path import dirname, join, normpath
this_folder = pathlib.Path (__file__).parent.resolve ()
find_and_replace_string_v2.start (
	the_path = str (this_folder) + "/DB",

	find = 'region 1',
	replace_with = 'region one',
	
	replace_contents = "yes",
	replace_paths = "yes"
)
```