## About
Applies a patch to the target file by searching for a sequence of bytes and substituting.


## Usage
```shell
sequence_patcher.py [--reverse] [--force] [--quiet] target patch
```
`target` - target file to patch  
`patch` - file containing one or more patches to apply  
`--reverse` - revert patch swapping match and replace bytes  
`--force` - skips warnings and applies patch to first match in target  
`--quiet` - hides all non-essential output  

## Patch file structure

```
[patch name|hexOffset]
bytes to match
bytes to substitute
```
`patch name` - a user-friendly name of the patch to apply  
`hexOffset` - a hex representation of where the patch should be located. optional. eg: `039AD2`  
`bytesToMatch` - the sequence of bytes to search for  
`bytesToSubstitute` - the sequence of bytes to write  
