Thwip is a Django back-end that imports a comic-archive collection and retrieves the appropriate metadata from [Comic Vine](https://comicvine.gamespot.com/api/), and provides a REST api that will allow you to read your comics. The React frontend can be found at [Thwip-Frontend](https://github.com/bpepple/thwip-frontend).

### Features ###
* Reads comic archives (cbz)
* REST API

### Note ###
Thwip is still in heavy development and not production-ready.

### Installation ###
If you want to hack on Thwip, here's some installation instructions: [Thwip Wiki](https://github.com/bpepple/thwip/wiki/Installation-on-Fedora-Linux).

### FAQ ###
1. Why must I tag my comics with [Comic Tagger](https://github.com/davide-romanini/comictagger) before I can import my comics?
    * Implementing comic issue search is fairly tough to do right, and frankly a tool dedicated to that is a better solution. The only information we need to import a comic is an issue's comic vine id, and as far as I'm aware Comic Tagger is the only tagging utility that includes that information. If you know others that do, drop me a note with the tag layout to parse and I'll add it to the project.
  
2. Why no cbr (rar) support?
    1. I'm not aware of any provider (Comixology, Humble Bundle, DriveThru Comics, etc.) of legally downloadable DRM-free comics that use the rar format.
    2. It's a non-free software file format.
    
3. Do you support pdf?
    * Don't have any plan to since you can't write tags to them, and I have no plans to include Comic Vine issue searching to the proejct.

4. Do you have a Docker installation?
    * Nope, but if you want to create one I'd be more than happy to look at a pull request. :smiley:
