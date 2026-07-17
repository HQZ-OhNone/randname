"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
logo_randname = r"""
                      _                            
  _ __ __ _ _ __   __| |_ __   __ _ _ __ ___   ___  
 | '__/ _` | '_ \ / _` | '_ \ / _` | '_ ` _ \ / _ \ 
 | | | (_| | | | | (_| | | | | (_| | | | | | |  __/ 
 |_|  \__,_|_| |_|\__,_|_| |_|\__,_|_| |_| |_|\___| 
---HQZ-OhNone <ohnone_hqz@outlook.com>
"""
print(logo_randname, end="\n\n")

from lib import importnames
from lib import Lift
from lib import Single
from lib import Multi

print("\ntest Single\n")
Single.Single(importnames.names)
print("test Multi\n\n")
Multi.Multi(importnames.names, 3)
print("test Lift\n")
a = Lift.Lift(importnames.names, importnames.names, 4)
b = Lift.Lift(importnames.names, a["Liftdict"], 6)
c = Lift.Lift(importnames.names, b["Liftdict"], 5)
Lift.Lift(importnames.names, c["Liftdict"], 2)


print("=> exit: randname")

