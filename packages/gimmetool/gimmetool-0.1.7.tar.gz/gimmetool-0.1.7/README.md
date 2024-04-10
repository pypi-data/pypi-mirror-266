# Gimme: The Multi-Repo Manager

This is a utility designed to help developers quickly hop between and manage the many repositories they keep on their workstations.

The main function of this util is jumping between repos with the base command, `gimme [repo]`, but it also provides a few other simple utils.

checkout `gimme -h` for more info.

## Setup

Out of the box, you'll need to tell gimme where your code lives. For example if your home looks like this:

```shell
/Users/bob/code:
  - frontend/
    - .git/
    - src/
    - etc...
  - backend/
    - .git/
    - src/
    - etc...
  - my-site/
    - .git/
    - src/
    - etc...
```

Then you'd add the `code` directory:

```shell
~$ gimme config add group /Users/bob/code
```

Then you should be able to hop between any repo under that folder:

```shell
~$ gimme front
~/code/frontend$ gimme back
~/code/backend$
```

## Other Tools
There are a few other tricks `gimme` has up its sleeve to streamline jumps between your most common repos. You can set up favorites, which are prioritized when searching on a keyword, as well as aliases for longer searches.

### Favorites

Let's say you have the following repos:
```shell
/Users/bob/code/
- jfe/
- jfe-apis/
- libjfe/
```

Jumping with `gimme jfe` might result in a jump to a repo you don't actually want to. 

```shell
~$ gimme jfe
~/code/jfe-apis$ # really? >:(
```

But, by adding the repo you want as a favorite, `gimme` will prioritize it.

```
gimme config add favorite /User/bob/code/jfe
```

Now, the jump is unambiguous:

```shell
~$ gimme jfe
~/code/jfe$ # :D
```

### Aliases

Sometimes, there are repos with longer names that you'd rather not change, but that you'd also rather not type.

```shell
/User/bob/code/legacy-backend-2018
```

You can create an alias that maps a shortcut to a more specific search.

```shell
~$ gimme config add alias back2018 legacy-backend-2018
```

Now, you don't have to type all that specific crap to get to the repo you want, and you don't have to change the name of the directory and eventually forget the name of the remote origin it actually belongs to.

```shell
~$ gimme back18
~/code/legacy-backend-2018$ 
```

### Mass Updates

A little tired of having to pull multiple times on a bunch of separate repos? `gimme` will update the default branch of every repo in your groups!

```
~$ gimme updates
- Updating 'layout-qualtrics-2018'...done
- Updating 'namespace-provisioning'...done
- Updating 'layout-qualtrics-2017'...done
- Updating 'aws-policies'...done
```
