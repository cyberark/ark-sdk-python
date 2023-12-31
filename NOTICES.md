# TABLE OF CONTENTS

The following is a listing of the ark-sdk-python open source components detailed
in this document. This list is provided for your convenience; please read
further if you wish to review the copyright notice(s) and the full text
of the license associated with each component.

- [SECTION 1: Apache / Apache-2.0](<SECTION-1:-Apache-/-Apache-2.0>)
  - https://github.com/psf/requests - [Requests](#Requests)
  - https://github.com/kislyuk/argcomplete - [Argcomplete](#Argcomplete)
  - https://github.com/mkorpela/overrides - [Overrides](#Overrides)
  - https://github.com/pypa/packaging - [Packaging](#Packaging)
  - https://github.com/fake-useragent/fake-useragent - [Fake-useragent](#Fake-useragent)
  - https://github.com/invl/retry - [Retry](#Retry)
  - https://github.com/dateutil/dateutil - [Dateutil](#Dateutil)

- [SECTION 2: BSD-2-Clause](<SECTION 2: BSD-2-Clause>)
  - https://github.com/Legrandin/pycryptodome - [Pycryptodome](#Pycryptodome)

- [SECTION 3: BSD-3-Clause](<SECTION 3: BSD-3-Clause>)
  - https://github.com/tartley/colorama - [Colorama](#Colorama)
  - https://github.com/uqfoundation/dill - [Dill](#Dill)

- [SECTION 4: MIT](<SECTION 4: MIT>)
  - https://github.com/jaraco/keyring - [Keyring](#Keyring)
  - https://github.com/frispete/keyrings.cryptfile - [Keyrings.cryptfile](#Keyrings.cryptfile)
  - https://github.com/pydantic/pydantic - [Pydantic](#Pydantic)
  - https://github.com/seperman/deepdiff - [Deepdiff](#Deepdiff)
  - https://github.com/lipoja/URLExtract - [URLExtract](#URLExtract)
  - https://github.com/magmax/python-inquirer - [Python-inquirer](#Python-inquirer)
  - https://github.com/tkem/cachetools - [Cachetools](#Cachetools)
  - https://github.com/mpdavis/python-jose - [Python-jose](#Python-jose)
  - https://github.com/regebro/tzlocal - [Tzlocal](#Tzlocal)
  - https://github.com/yaml/pyyaml - [Pyyaml](#Pyyaml)

- [SECTION 5: ISC](<SECTION 5: ISC>)
  - https://github.com/verigak/progress - [Progress](#Progress)


# SECTION 1: Apache / Apache-2.0

## Requests

https://github.com/psf/requests

### Authors / Copyright

Requests was lovingly created by Kenneth Reitz.

Keepers of the Crystals
- Nate Prewitt `@nateprewitt <https://github.com/nateprewitt>`_.
- Seth M. Larson `@sethmlarson <https://github.com/sethmlarson>`_.

Previous Keepers of Crystals
- Kenneth Reitz <me@kennethreitz.org> `@ken-reitz <https://github.com/ken-reitz>`_, reluctant Keeper of the Master Crystal.
- Cory Benfield <cory@lukasa.co.uk> `@lukasa <https://github.com/lukasa>`_
- Ian Cordasco <graffatcolmingov@gmail.com> `@sigmavirus24 <https://github.com/sigmavirus24>`_.


Patches and Suggestions
- Various Pocoo Members
- Chris Adams
- Flavio Percoco Premoli
- Dj Gilcrease
- Justin Murphy
- Rob Madole
- Aram Dulyan
- Johannes Gorset
- 村山めがね (Megane Murayama)
- James Rowe
- Daniel Schauenberg
- Zbigniew Siciarz
- Daniele Tricoli 'Eriol'
- Richard Boulton
- Miguel Olivares <miguel@moliware.com>
- Alberto Paro
- Jérémy Bethmont
- 潘旭 (Xu Pan)
- Tamás Gulácsi
- Rubén Abad
- Peter Manser
- Jeremy Selier
- Jens Diemer
- Alex (`@alopatin <https://github.com/alopatin>`_)
- Tom Hogans <tomhsx@gmail.com>
- Armin Ronacher
- Shrikant Sharat Kandula
- Mikko Ohtamaa
- Den Shabalin
- Daniel Miller <danielm@vs-networks.com>
- Alejandro Giacometti
- Rick Mak
- Johan Bergström
- Josselin Jacquard
- Travis N. Vaught
- Fredrik Möllerstrand
- Daniel Hengeveld
- Dan Head
- Bruno Renié
- David Fischer
- Joseph McCullough
- Juergen Brendel
- Juan Riaza
- Ryan Kelly
- Rolando Espinoza La fuente
- Robert Gieseke
- Idan Gazit
- Ed Summers
- Chris Van Horne
- Christopher Davis
- Ori Livneh
- Jason Emerick
- Bryan Helmig
- Jonas Obrist
- Lucian Ursu
- Tom Moertel
- Frank Kumro Jr
- Chase Sterling
- Marty Alchin
- takluyver
- Ben Toews (`@mastahyeti <https://github.com/mastahyeti>`_)
- David Kemp
- Brendon Crawford
- Denis (`@Telofy <https://github.com/Telofy>`_)
- Matt Giuca
- Adam Tauber
- Honza Javorek
- Brendan Maguire <maguire.brendan@gmail.com>
- Chris Dary
- Danver Braganza <danverbraganza@gmail.com>
- Max Countryman
- Nick Chadwick
- Jonathan Drosdeck
- Jiri Machalek
- Steve Pulec
- Michael Kelly
- Michael Newman <newmaniese@gmail.com>
- Jonty Wareing <jonty@jonty.co.uk>
- Shivaram Lingamneni
- Miguel Turner
- Rohan Jain (`@crodjer <https://github.com/crodjer>`_)
- Justin Barber <barber.justin@gmail.com>
- Roman Haritonov (`@reclosedev <https://github.com/reclosedev>`_)
- Josh Imhoff <joshimhoff13@gmail.com>
- Arup Malakar <amalakar@gmail.com>
- Danilo Bargen (`@dbrgn <https://github.com/dbrgn>`_)
- Torsten Landschoff
- Michael Holler (`@apotheos <https://github.com/apotheos>`_)
- Timnit Gebru
- Sarah Gonzalez
- Victoria Mo
- Leila Muhtasib
- Matthias Rahlf <matthias@webding.de>
- Jakub Roztocil <jakub@roztocil.name>
- Rhys Elsmore
- André Graf (`@dergraf <https://github.com/dergraf>`_)
- Stephen Zhuang (`@everbird <https://github.com/everbird>`_)
- Martijn Pieters
- Jonatan Heyman
- David Bonner <dbonner@gmail.com> (`@rascalking <https://github.com/rascalking>`_)
- Vinod Chandru
- Johnny Goodnow <j.goodnow29@gmail.com>
- Denis Ryzhkov <denisr@denisr.com>
- Wilfred Hughes <me@wilfred.me.uk>
- Dmitry Medvinsky <me@dmedvinsky.name>
- Bryce Boe <bbzbryce@gmail.com> (`@bboe <https://github.com/bboe>`_)
- Colin Dunklau <colin.dunklau@gmail.com> (`@cdunklau <https://github.com/cdunklau>`_)
- Bob Carroll <bob.carroll@alum.rit.edu> (`@rcarz <https://github.com/rcarz>`_)
- Hugo Osvaldo Barrera <hugo@barrera.io> (`@hobarrera <https://github.com/hobarrera>`_)
- Łukasz Langa <lukasz@langa.pl>
- Dave Shawley <daveshawley@gmail.com>
- James Clarke (`@jam <https://github.com/jam>`_)
- Kevin Burke <kev@inburke.com>
- Flavio Curella
- David Pursehouse <david.pursehouse@gmail.com> (`@dpursehouse <https://github.com/dpursehouse>`_)
- Jon Parise (`@jparise <https://github.com/jparise>`_)
- Alexander Karpinsky (`@homm86 <https://twitter.com/homm86>`_)
- Marc Schlaich (`@schlamar <https://github.com/schlamar>`_)
- Park Ilsu <daftonshady@gmail.com> (`@daftshady <https://github.com/daftshady>`_)
- Matt Spitz (`@mattspitz <https://github.com/mattspitz>`_)
- Vikram Oberoi (`@voberoi <https://github.com/voberoi>`_)
- Can Ibanoglu <can.ibanoglu@gmail.com> (`@canibanoglu <https://github.com/canibanoglu>`_)
- Thomas Weißschuh <thomas@t-8ch.de> (`@t-8ch <https://github.com/t-8ch>`_)
- Jayson Vantuyl <jayson@aggressive.ly>
- Pengfei.X <pengphy@gmail.com>
- Kamil Madac <kamil.madac@gmail.com>
- Michael Becker <mike@beckerfuffle.com> (`@beckerfuffle <https://twitter.com/beckerfuffle>`_)
- Erik Wickstrom <erik@erikwickstrom.com> (`@erikwickstrom <https://github.com/erikwickstrom>`_)
- Константин Подшумок (`@podshumok <https://github.com/podshumok>`_)
- Ben Bass (`@codedstructure <https://github.com/codedstructure>`_)
- Jonathan Wong <evolutionace@gmail.com> (`@ContinuousFunction <https://github.com/ContinuousFunction>`_)
- Martin Jul (`@mjul <https://github.com/mjul>`_)
- Joe Alcorn (`@buttscicles <https://github.com/buttscicles>`_)
- Syed Suhail Ahmed <ssuhail.ahmed93@gmail.com> (`@syedsuhail <https://github.com/syedsuhail>`_)
- Scott Sadler (`@ssadler <https://github.com/ssadler>`_)
- Arthur Darcet (`@arthurdarcet <https://github.com/arthurdarcet>`_)
- Ulrich Petri (`@ulope <https://github.com/ulope>`_)
- Muhammad Yasoob Ullah Khalid <yasoob.khld@gmail.com> (`@yasoob <https://github.com/yasoob>`_)
- Paul van der Linden (`@pvanderlinden <https://github.com/pvanderlinden>`_)
- Colin Dickson (`@colindickson <https://github.com/colindickson>`_)
- Smiley Barry (`@smiley <https://github.com/smiley>`_)
- Shagun Sodhani (`@shagunsodhani <https://github.com/shagunsodhani>`_)
- Robin Linderborg (`@vienno <https://github.com/vienno>`_)
- Brian Samek (`@bsamek <https://github.com/bsamek>`_)
- Dmitry Dygalo (`@Stranger6667 <https://github.com/Stranger6667>`_)
- piotrjurkiewicz
- Jesse Shapiro <jesse@jesseshapiro.net> (`@haikuginger <https://github.com/haikuginger>`_)
- Nate Prewitt <nate.prewitt@gmail.com> (`@nateprewitt <https://github.com/nateprewitt>`_)
- Maik Himstedt
- Michael Hunsinger
- Brian Bamsch <bbamsch32@gmail.com> (`@bbamsch <https://github.com/bbamsch>`_)
- Om Prakash Kumar <omprakash070@gmail.com> (`@iamprakashom <https://github.com/iamprakashom>`_)
- Philipp Konrad <gardiac2002@gmail.com> (`@gardiac2002 <https://github.com/gardiac2002>`_)
- Hussain Tamboli <hussaintamboli18@gmail.com> (`@hussaintamboli <https://github.com/hussaintamboli>`_)
- Casey Davidson (`@davidsoncasey <https://github.com/davidsoncasey>`_)
- Andrii Soldatenko (`@a_soldatenko <https://github.com/andriisoldatenko>`_)
- Moinuddin Quadri <moin18@gmail.com> (`@moin18 <https://github.com/moin18>`_)
- Matt Kohl (`@mattkohl <https://github.com/mattkohl>`_)
- Jonathan Vanasco (`@jvanasco <https://github.com/jvanasco>`_)
- David Fontenot (`@davidfontenot <https://github.com/davidfontenot>`_)
- Shmuel Amar (`@shmuelamar <https://github.com/shmuelamar>`_)
- Gary Wu (`@garywu <https://github.com/garywu>`_)
- Ryan Pineo (`@ryanpineo <https://github.com/ryanpineo>`_)
- Ed Morley (`@edmorley <https://github.com/edmorley>`_)
- Matt Liu <liumatt@gmail.com> (`@mlcrazy <https://github.com/mlcrazy>`_)
- Taylor Hoff <primdevs@protonmail.com> (`@PrimordialHelios <https://github.com/PrimordialHelios>`_)
- Arthur Vigil (`@ahvigil <https://github.com/ahvigil>`_)
- Nehal J Wani (`@nehaljwani <https://github.com/nehaljwani>`_)
- Demetrios Bairaktaris (`@DemetriosBairaktaris <https://github.com/demetriosbairaktaris>`_)
- Darren Dormer (`@ddormer <https://github.com/ddormer>`_)
- Rajiv Mayani (`@mayani <https://github.com/mayani>`_)
- Antti Kaihola (`@akaihola <https://github.com/akaihola>`_)
- "Dull Bananas" <dull.bananas0@gmail.com> (`@dullbananas <https://github.com/dullbananas>`_)
- Alessio Izzo (`@aless10 <https://github.com/aless10>`_)
- Sylvain Marié (`@smarie <https://github.com/smarie>`_)
- Hod Bin Noon (`@hodbn <https://github.com/hodbn>`_)
- Mike Fiedler (`@miketheman <https://github.com/miketheman>`_)

### License

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
         Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
         stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
         that You distribute, all copyright, patent, trademark, and
         attribution notices from the Source form of the Work,
         excluding those notices that do not pertain to any part of
         the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
         distribution, then any Derivative Works that You distribute must
         include a readable copy of the attribution notices contained
         within such NOTICE file, excluding those notices that do not
         pertain to any part of the Derivative Works, in at least one
         of the following places: within a NOTICE text file distributed
         as part of the Derivative Works; within the Source form or
         documentation, if provided along with the Derivative Works; or,
         within a display generated by the Derivative Works, if and
         wherever such third-party notices normally appear. The contents
         of the NOTICE file are for informational purposes only and
         do not modify the License. You may add Your own attribution
         notices within Derivative Works that You distribute, alongside
         or as an addendum to the NOTICE text from the Work, provided
         that such additional attribution notices cannot be construed
         as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.


## Argcomplete

https://github.com/kislyuk/argcomplete

### Authors / Copyright

Copyright 2012-2023, Andrey Kislyuk and argcomplete contributors

### License

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
         Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
         stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
         that You distribute, all copyright, patent, trademark, and
         attribution notices from the Source form of the Work,
         excluding those notices that do not pertain to any part of
         the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
         distribution, then any Derivative Works that You distribute must
         include a readable copy of the attribution notices contained
         within such NOTICE file, excluding those notices that do not
         pertain to any part of the Derivative Works, in at least one
         of the following places: within a NOTICE text file distributed
         as part of the Derivative Works; within the Source form or
         documentation, if provided along with the Derivative Works; or,
         within a display generated by the Derivative Works, if and
         wherever such third-party notices normally appear. The contents
         of the NOTICE file are for informational purposes only and
         do not modify the License. You may add Your own attribution
         notices within Derivative Works that You distribute, alongside
         or as an addendum to the NOTICE text from the Work, provided
         that such additional attribution notices cannot be construed
         as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS


## Overrides

https://github.com/mkorpela/overrides

### Authors / Copyright

This project exists only through the work of all the people who contribute.

mkorpela, drorasaf, ngoodman90, TylerYep, leeopop, donpatrice, jayvdb, joelgrus, lisyarus, soulmerge, rkr-at-dbx, ashwin153, brentyi, jobh, tjsmart, bersbersbers, LysanderGG

### License

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
         Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
         stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
         that You distribute, all copyright, patent, trademark, and
         attribution notices from the Source form of the Work,
         excluding those notices that do not pertain to any part of
         the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
         distribution, then any Derivative Works that You distribute must
         include a readable copy of the attribution notices contained
         within such NOTICE file, excluding those notices that do not
         pertain to any part of the Derivative Works, in at least one
         of the following places: within a NOTICE text file distributed
         as part of the Derivative Works; within the Source form or
         documentation, if provided along with the Derivative Works; or,
         within a display generated by the Derivative Works, if and
         wherever such third-party notices normally appear. The contents
         of the NOTICE file are for informational purposes only and
         do not modify the License. You may add Your own attribution
         notices within Derivative Works that You distribute, alongside
         or as an addendum to the NOTICE text from the Work, provided
         that such additional attribution notices cannot be construed
         as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "{}"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright {yyyy} {name of copyright owner}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


## Packaging

https://github.com/pypa/packaging

### Authors / Copyright

Copyright (c) Donald Stufft and individual contributors.

### License

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
         Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
         stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
         that You distribute, all copyright, patent, trademark, and
         attribution notices from the Source form of the Work,
         excluding those notices that do not pertain to any part of
         the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
         distribution, then any Derivative Works that You distribute must
         include a readable copy of the attribution notices contained
         within such NOTICE file, excluding those notices that do not
         pertain to any part of the Derivative Works, in at least one
         of the following places: within a NOTICE text file distributed
         as part of the Derivative Works; within the Source form or
         documentation, if provided along with the Derivative Works; or,
         within a display generated by the Derivative Works, if and
         wherever such third-party notices normally appear. The contents
         of the NOTICE file are for informational purposes only and
         do not modify the License. You may add Your own attribution
         notices within Derivative Works that You distribute, alongside
         or as an addendum to the NOTICE text from the Work, provided
         that such additional attribution notices cannot be construed
         as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS


## Fake-useragent

https://github.com/fake-useragent/fake-useragent

### Authors / Copyright

fake-useragent contributors

Author/maintainer:

    Melroy van den Berg @melroy89 <melroy@melroy.org>

Original author:

    Victor Kovtun @hellysmile <hellysmile@gmail.com>

Contributors:

    Alexey Shablevskiy @pcinkh <pcinkh@gmail.com>
    Christian Clauss @cclauss
    Jordan Vuong @Jordan9675
    Mohamad Nour Chawich @mochawich
    Simon Wenmouth @simon-wenmouth

    <Please alphabetize new entries>

### License

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
         Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
         stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
         that You distribute, all copyright, patent, trademark, and
         attribution notices from the Source form of the Work,
         excluding those notices that do not pertain to any part of
         the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
         distribution, then any Derivative Works that You distribute must
         include a readable copy of the attribution notices contained
         within such NOTICE file, excluding those notices that do not
         pertain to any part of the Derivative Works, in at least one
         of the following places: within a NOTICE text file distributed
         as part of the Derivative Works; within the Source form or
         documentation, if provided along with the Derivative Works; or,
         within a display generated by the Derivative Works, if and
         wherever such third-party notices normally appear. The contents
         of the NOTICE file are for informational purposes only and
         do not modify the License. You may add Your own attribution
         notices within Derivative Works that You distribute, alongside
         or as an addendum to the NOTICE text from the Work, provided
         that such additional attribution notices cannot be construed
         as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright (c) hellysmile@gmail.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


## Retry

https://github.com/invl/retry

### Authors / Copyright

Copyright 2014 invl

### License

Copyright 2014 invl

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


## Dateutil

https://github.com/dateutil/dateutil

### Authors / Copyright

Contributors (alphabetical order)
Adam Chainz adam@MASKED
Adrien Cossa cossa@MASKED
Alec Nikolas Reiter alecreiter@MASKED
Alec Reiter areiter@MASKED
Aleksei Strizhak alexei.mifrill.strizhak@MASKED (gh: @Mifrill)
Alex Chamberlain (gh: @alexchamberlain) D
Alex Verdyan verdyan@MASKED
Alex Willmer alex@moreati.org.uk (gh: @moreati) R
Alexander Brugh alexander.brugh@MASKED (gh: @abrugh)
Alexander Shadchin alexandr.shadchin@gmail.com (gh: @shadchin) D
Alistair McMaster alistair@MASKED (gh: @alimcmaster1 ) D
Allison Quinlan aquinlan82@gmail.com (gh: @aquinlan) D
Andrew Bennett (gh: @andrewcbennett) D
Andrew Murray radarhere@MASKED
Arclight arclight@MASKED (gh: @arclightslavik)
Aritro Nandi gurgenz221@gmail.com (gh: @gurgenz221) D
Bernat Gabor bgabor8@bloomberg.net (gh: @gaborbernat) D
Bradlee Speice bradlee@speice.io (gh: @bspeice) D
Brandon W Maister quodlibetor@MASKED
Brock Mendel jbrockmendel@MASKED (gh: @jbrockmendel) R
Brook Li (gh: @absreim) D
Carlos carlosxl@MASKED
Cheuk Ting Ho cheukting.ho@gmail.com (gh: @cheukting) D
Chris van den Berg (gh: bergvca) D
Christopher Cordero ccordero@pm.me (gh: cs-cordero) D
Christopher Corley cscorley@MASKED
Claudio Canepa ccanepacc@MASKED
Corey Girard corey.r.girard@gmail.com (gh: @coreygirard) D
Cosimo Lupo cosimo@anthrotype.com (gh: @anthrotype) D
Daniel Lemm (gh: @ffe4) D
Daniel Lepage dplepage@MASKED
David Lehrian david@MASKED
Dean Allsopp (gh: @daplantagenet) D
Dominik Kozaczko dominik@MASKED
Elliot Hughes elliot.hughes@gmail.com (gh: @ElliotJH) D
Elvis Pranskevichus el@MASKED
Fan Huang fanhuang.scb@gmail.com(gh: @fhuang5) D
Florian Rathgeber (gh: @kynan) D
Gabriel Bianconi gabriel@MASKED (gh: @GabrielBianconi) D
Gabriel Poesia gabriel.poesia@MASKED
Gökçen Nurlu gnurlu1@bloomberg.net (gh: @gokcennurlu) D
Grant Garrett-Grossman grantlycee@gmail.com (gh: @FakeNameSE) D
Gustavo Niemeyer gustavo@niemeyer.net (gh: @niemeyer)
Holger Joukl holger.joukl@MASKED (gh: @hjoukl)
Hugo van Kemenade (gh: @hugovk) D
Igor mrigor83@MASKED
Ionuț Ciocîrlan jdxlark@MASKED
Jacqueline Chen jacqueline415@outlook.com (gh: @jachen20) D
Jake Chorley (gh: @jakec-github) D
Jakub Kulík (gh: @kulikjak) D
Jan Studený jendas1@MASKED
Jay Weisskopf jay@jayschwa.net (gh: @jayschwa) D
Jitesh jitesh@MASKED
John Purviance jpurviance@MASKED (gh @jpurviance) D
Jon Dufresne jon.dufresne@MASKED (gh: @jdufresne) R
Jonas Neubert jonas@MASKED (gh: @jonemo) R
Kevin Nguyen kvn219@MASKED D
Kirit Thadaka kirit.thadaka@gmail.com (gh: @kirit93) D
Kubilay Kocak koobs@MASKED
Laszlo Kiss Kollar kiss.kollar.laszlo@MASKED (gh: @lkollar) D
Lauren Oldja oldja@MASKED (gh: @loldja) D
Luca Ferocino luca.ferox@MASKED (gh: @lucaferocino) D
Mario Corchero mcorcherojim@MASKED (gh: @mariocj89) R
Mark Bailey msb@MASKED D
Mateusz Dziedzic (gh: @m-dz) D
Matt Cooper vtbassmatt@MASKED (gh: @vtbassmatt) D
Matthew Schinckel matt@MASKED
Max Shenfield shenfieldmax@MASKED
Maxime Lorant maxime.lorant@MASKED
Michael Aquilina michaelaquilina@MASKED (gh: @MichaelAquilina)
Michael J. Schultz mjschultz@MASKED
Michael Käufl (gh: @michael-k)
Mike Gilbert floppym@MASKED
Nicholas Herrriot Nicholas.Herriot@gmail.com D
Nicolas Évrard (gh: @nicoe) D
Nick Smith nick.smith@MASKED
Orson Adams orson.network@MASKED (gh: @parsethis) D
Paul Brown (gh: @pawl) D
Paul Dickson (gh @prdickson) D
Paul Ganssle paul@ganssle.io (gh: @pganssle) R
Pascal van Kooten kootenpv@MASKED (gh: @kootenpv) R
Pavel Ponomarev comrad.awsum@MASKED
Peter Bieringer pb@MASKED
Pierre Gergondet pierre.gergondet@MASKED (gh: @gergondet) D
Quentin Pradet quentin@MASKED
Raymond Cha (gh: @weatherpattern) D
Ridhi Mahajan ridhikmahajan@MASKED D
Robin Henriksson Törnström <gh: @MrRawbin> D
Roy Williams rwilliams@MASKED
Rustem Saiargaliev (gh: @amureki) D
Satyabrat Bhol satyabrat35@MASKED (gh: @Satyabrat35) D
Savraj savraj@MASKED
Sergey Vishnikin armicron@MASKED
Sherry Zhou (gh: @cssherry) D
Siping Meng (gh: @smeng10) D
Stefan Bonchev D
Thierry Bastian thierryb@MASKED
Thomas A Caswell tcaswell@MASKED (gh: @tacaswell) R
Thomas Achtemichuk tom@MASKED
Thomas Grainger tagrain@gmail.com (gh: @graingert) D
Thomas Kluyver takowl@MASKED (gh: @takluyver)
Tim Gates tim.gates@iress.com (gh: timgates42)
Tomasz Kluczkowski (gh: @Tomasz-Kluczkowski) D
Tomi Pieviläinen tomi.pievilainen@iki.fi
Unrud Unrud@MASKED (gh: @unrud)
Xavier Lapointe lapointe.xavier@MASKED (gh: @lapointexavier) D
X O xo@MASKED
Yaron de Leeuw me@jarondl.net (gh: @jarondl)
Yoney alper_yoney@hotmail.com D
Yuan Huang huangy22@gmail.com (gh: @huangy22) D
Zbigniew Jędrzejewski-Szmek zbyszek@MASKED
bachmann bachmann.matt@MASKED
bjv brandon.vanvaerenbergh@MASKED (@bjamesvERT)
gl gl@MASKED
gfyoung gfyoung17@gmail.com D
Labrys labrys.git@gmail.com (gh: @labrys) R
ms-boom ms-boom@MASKED
ryanss ryanssdev@MASKED (gh: @ryanss) R

### License

Copyright 2017- Paul Ganssle <paul@ganssle.io>
Copyright 2017- dateutil contributors (see AUTHORS file)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

The above license applies to all contributions after 2017-12-01, as well as
all contributions that have been re-licensed (see AUTHORS file for the list of
contributors who have re-licensed their code).

dateutil - Extensions to the standard Python datetime module.

Copyright (c) 2003-2011 - Gustavo Niemeyer <gustavo@niemeyer.net>
Copyright (c) 2012-2014 - Tomi Pieviläinen <tomi.pievilainen@iki.fi>
Copyright (c) 2014-2016 - Yaron de Leeuw <me@jarondl.net>
Copyright (c) 2015-     - Paul Ganssle <paul@ganssle.io>
Copyright (c) 2015-     - dateutil contributors (see AUTHORS file)

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The above BSD License Applies to all code, even that also covered by Apache 2.0.



# SECTION 2: BSD-2-Clause

## Pycryptodome

https://github.com/Legrandin/pycryptodome

### Authors / Copyright

Simon Arneaud Nevins Bartolomeo Thorsten E. Behrens Tim Berners-Lee Frédéric Bertolus Ian Bicking Joris Bontje Antoon Bosselaers Andrea Bottoni Jean-Paul Calderone Sergey Chernov Geremy Condra Jan Dittberner Andrew Eland Philippe Frycia Peter Gutmann Hirendra Hindocha Nikhil Jhingan Sebastian Kayser Ryan Kelly Andrew M. Kuchling Piers Lauder Legrandin M.-A. Lemburg Wim Lewis Darsey C. Litzenberger Richard Mitchell Mark Moraes Lim Chee Siang Bryan Olson Wallace Owen Colin Plumb Robey Pointer Lorenz Quack Sebastian Ramacher Jeethu Rao James P. Rutledge Matt Schreiner Peter Simmons Janne Snabb Tom St. Denis Anders Sundman Paul Swartz Fabrizio Tarizzo Kevin M. Turner Barry A. Warsaw Eric Young Hannes van Niekerk Stefan Seering Koki Takahashi Lauro de Lima

### License

The source code in PyCryptodome is partially in the public domain
and partially released under the BSD 2-Clause license.

In either case, there are minimal if no restrictions on the redistribution,
modification and usage of the software.

Public domain

All code originating from  PyCrypto is free and unencumbered software
released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org>

BSD license

All direct contributions to PyCryptodome are released under the following
license. The copyright of each piece belongs to the respective author.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# SECTION 3: BSD-3-Clause

## Colorama

https://github.com/tartley/colorama

### Authors / Copyright

Copyright Jonathan Hartley & Arnon Yaari, 2013-2020. BSD 3-Clause license; see LICENSE file.

### License

Copyright (c) 2010 Jonathan Hartley
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holders, nor those of its contributors
  may be used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## Dill

https://github.com/uqfoundation/dill

### Authors / Copyright

M.M. McKerns, L. Strand, T. Sullivan, A. Fang, M.A.G. Aivazis,
"Building a framework for predictive science", Proceedings of
the 10th Python in Science Conference, 2011;
http://arxiv.org/pdf/1202.1056

Michael McKerns and Michael Aivazis,
"pathos: a framework for heterogeneous computing", 2010- ;
https://uqfoundation.github.io/project/pathos

### License

Copyright (c) 2004-2016 California Institute of Technology.
Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
All rights reserved.

This software is available subject to the conditions and terms laid
out below. By downloading and using this software you are agreeing
to the following conditions.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

- Neither the names of the copyright holders nor the names of any of
  the contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.




# SECTION 4: MIT

## Keyring

https://github.com/jaraco/keyring

### Authors / Copyright

author = Kang Zhang
author_email = jobo.zh@gmail.com
maintainer = Jason R. Coombs
maintainer_email = jaraco@jaraco.com

### License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.


## Keyrings.cryptfile

https://github.com/frispete/keyrings.cryptfile

### Authors / Copyright

Copyright (c) 2016-2018, Hans-Peter Jansen

### License

The MIT License (MIT)

Copyright (c) 2016-2018, Hans-Peter Jansen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Pydantic

https://github.com/pydantic/pydantic

### Authors / Copyright

Copyright (c) 2017 to present Pydantic Services Inc. and individual contributors.

authors = [
    {name = 'Samuel Colvin', email = 's@muelcolvin.com'},
    {name = 'Eric Jolibois', email = 'em.jolibois@gmail.com'},
    {name = 'Hasan Ramezani', email = 'hasan.r67@gmail.com'},
    {name = 'Adrian Garcia Badaracco', email = '1755071+adriangb@users.noreply.github.com'},
    {name = 'Terrence Dorsey', email = 'terry@pydantic.dev'},
    {name = 'David Montague', email = 'david@pydantic.dev'},
    {name = 'Serge Matveenko', email = 'lig@countzero.co'},
    {name = 'Marcelo Trylesinski', email = 'marcelotryle@gmail.com'},
    {name = 'Sydney Runkle', email = 'sydneymarierunkle@gmail.com'},
    {name = 'David Hewitt', email = 'mail@davidhewitt.io'},
]

### License

The MIT License (MIT)

Copyright (c) 2017 to present Pydantic Services Inc. and individual contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Deepdiff

https://github.com/seperman/deepdiff

### Authors / Copyright

Dehpour, S. (2023). DeepDiff (Version 6.7.1) [Software]. Available from https://github.com/seperman/deepdiff.

Authors in order of the timeline of their contributions:

Sep Dehpour (Seperman)
Victor Hahn Castell for the tree view and major contributions:
nfvs for Travis-CI setup script.
brbsix for initial Py3 porting.
WangFenjin for unicode support.
timoilya for comparing list of sets when ignoring order.
Bernhard10 for significant digits comparison.
b-jazz for PEP257 cleanup, Standardize on full names, fixing line endings.
finnhughes for fixing slots
moloney for Unicode vs. Bytes default
serv-inc for adding help(deepdiff)
movermeyer for updating docs
maxrothman for search in inherited class attributes
maxrothman for search for types/objects
MartyHub for exclude regex paths
sreecodeslayer for DeepSearch match_string
Brian Maissy brianmaissy for weakref fix, enum tests
Bartosz Borowik boba-2 for Exclude types fix when ignoring order
Brian Maissy brianmaissy for fixing classes which inherit from classes with slots didn't have all of their slots compared
Juan Soler Soleronline for adding ignore_type_number
mthaddon for adding timedelta diffing support
Necrophagos for Hashing of the number 1 vs. True
gaal-dev for adding exclude_obj_callback
Ivan Piskunov van-ess0 for deprecation warning enhancement.
Michał Karaś MKaras93 for the pretty view
Christian Kothe chkothe for the basic support for diffing numpy arrays
Timothy for truncate_datetime
d0b3rm4n for bugfix to not apply format to non numbers.
MyrikLD for Bug Fix NoneType in ignore type groups
Stian Jensen stianjensen for improving ignoring of NoneType in diff
Florian Klien flowolf for adding math_epsilon
Tim Klein timjklein36 for retaining the order of multiple dictionary items added via Delta.
Wilhelm Schürmannwbsch for fixing the typo with yml files.
lyz-code for adding support for regular expressions in DeepSearch and strict_checking feature in DeepSearch.
dtorres-sf for adding the option for custom compare function
Tony Wang Tony-Wang for bugfix: verbose_level==0 should disable values_changes.
Sun Ao eggachecat for adding custom operators.
Sun Ao eggachecat for adding ignore_order_func.
SlavaSkvortsov for fixing unprocessed key error.
Håvard Thom havardthom for adding UUID support.
Dhanvantari Tilak Dhanvantari for Bug-Fix: TypeError in _get_numbers_distance() when ignore_order = True.
Yael Mintz yaelmi3 for detailed pretty print when verbose_level=2.
Mikhail Khviyuzov mskhviyu for Exclude obj callback strict.
dtorres-sf for the fix for diffing using iterable_compare_func with nested objects.
Enric Pou for bug fix of ValueError when using Decimal 0.x
Uwe Fladrich for fixing bug when diff'ing non-sequence iterables
Michal Ozery-Flato for setting equal_nan=ignore_nan_inequality in the call for np.array_equal
martin-kokos for using Pytest's tmp_path fixture instead of /tmp/
Håvard Thom havardthom for adding include_obj_callback and include_obj_callback_strict.
Noam Gottlieb for fixing a corner case where numpy's np.float32 nans are not ignored when using ignore_nan_equality.
maggelus for the bugfix deephash for paths.
maggelus for the bugfix deephash compiled regex.
martin-kokos for fixing the tests dependent on toml.
kor4ik for the bugfix for include_paths for nested dictionaries.
martin-kokos for using tomli and tomli-w for dealing with tomli files.
Alex Sauer-Budge for the bugfix for datetime.date.
William Jamieson for NumPy 2.0 compatibility

### License

The MIT License (MIT)

Copyright (c) 2014 - 2021 Sep Dehpour (Seperman) and contributors
www.zepworks.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## URLExtract

https://github.com/lipoja/URLExtract

### Authors / Copyright

author="Jan Lipovský",
author_email="janlipovsky@gmail.com",

### License

The MIT License (MIT)

Copyright (c) 2016 Jan Lipovský

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Python-inquirer

https://github.com/magmax/python-inquirer

### Authors / Copyright

Copyright (c) 2014-2023 Miguel Ángel García (@magmax_en), based on Inquirer.js, by Simon Boudrias (@vaxilart)

### License

The MIT License (MIT)

Copyright (c) 2014 Miguel Ángel García

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Cachetools

https://github.com/tkem/cachetools

## Authors / Copyright

Copyright (c) 2014-2023 Thomas Kemmer.

### License

The MIT License (MIT)

Copyright (c) 2014-2022 Thomas Kemmer

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Python-jose

https://github.com/mpdavis/python-jose

### Authors / Copyright

author = Michael Davis
author_email = mike.philip.davis@gmail.com

### License

The MIT License (MIT)

Copyright (c) 2015 Michael Davis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Tzlocal

https://github.com/regebro/tzlocal

### Authors / Copyright

Maintainer

Lennart Regebro, regebro@gmail.com

Contributors

Marc Van Olmen
Benjamen Meyer
Manuel Ebert
Xiaokun Zhu
Cameris
Edward Betts
McK KIM
Cris Ewing
Ayala Shachar
Lev Maximov
Jakub Wilk
John Quarles
Preston Landers
Victor Torres
Jean Jordaan
Zackary Welch
Mickaël Schoentgen
Gabriel Corona
Alex Grönholm
Julin S
Miroslav Šedivý
revansSZ
Sam Treweek
Peter Di Pasquale
Rongrong

Copyright 2011-2017 Lennart Regebro

### License

Copyright 2011-2017 Lennart Regebro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Pyyaml

https://github.com/yaml/pyyaml

### Authors / Copyright

The PyYAML module was written by Kirill Simonov xi@resolvent.net. It is currently maintained by the YAML and Python communities.

Copyright (c) 2017-2021 Ingy döt Net
Copyright (c) 2006-2016 Kirill Simonov

### License

Copyright (c) 2017-2021 Ingy döt Net
Copyright (c) 2006-2016 Kirill Simonov

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


# SECTION 5: ISC

## Progress

https://github.com/verigak/progress

### Authors / Copyright

progress is licensed under ISC

Copyright (c) 2012 Georgios Verigakis <verigak@gmail.com>

### License

Copyright (c) 2012 Georgios Verigakis <verigak@gmail.com>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
