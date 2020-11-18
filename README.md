# Lestrade TEI Tagger
Lestrade TEI Tagger takes plain text and turns it into a TEI-tagged document. It uses Mathematica/Wolfram
Language's text entity recognition system to detect entities to be tagged. The end goal is to use
Wolfram Language entity data to extract additional information about tagged entities.

Lestrade TEI Tagger is based off of Audrey Holmes' [Historical Markup Tool](http://www.historical-markup.com),
which used Flair to detect entities.

# Entity ref URI scheme
If Mathematica thinks a text entity has a Wolfram Language entity interpretation, then the text entity's TEI
tag will have a @ref attribute that is a URI with the following schema:
```
urn:WolframEntity:WOLFRAM_ENTITY_TYPE:WOLFRAM_ENTITY_CANONICAL_NAME
```
Note: `WOLFRAM_ENTITY_CANONICAL_NAME` is **allowed to contain colons!** Since it's the last part of
the URN scheme, you know that anything that comes after the 3rd colon is part of the canonical name.
The `WOLFRAM_ENTITY_CANONICAL_NAME` is also encoded with HTML entities so that it can safely be used
as an XML attribute value. (Example: `urn:WolframEntity:Building:&quot;GreatPyramidOfGiza::jbm66&quot;`)

Using the URN, you should be able to reconstruct the original Wolfram Language Entity with Mathematica.
Decode `WOLFRAM_ENTITY_CANONICAL_NAME` into ASCII characters and use `Entity[WOLFRAM_ENTITY_TYPE, WOLFRAM_ENTITY_CANONICAL_NAME]`.
(Example: `Entity["Building","GreatPyramidOfGiza::jbm66"]`.)