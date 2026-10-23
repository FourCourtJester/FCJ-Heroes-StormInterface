Anything in here is copied to the build as-is and served from the root.

`public/logos/home.svg` is `./logos/home.svg` in a component — a relative path, so it
keeps working wherever the studio is deployed.

For images an operator adds during a show, use the image store in the board's header
instead. Those live with the show rather than with the build, so they can change
without a redeploy and reach every machine in the room.
