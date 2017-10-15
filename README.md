# TextIT

The idea for this project is recognizing handwritten text in images and producing a txt plain text output with one particular restriction: keep the text positions on the same place.

For the backend we used Python and Flask. To carry out the handwritten text recognition we used the [Microsoft Azure Computer Vision API](https://azure.microsoft.com/services/cognitive-services/computer-vision/).

As neither of us had much experience with frontend, we decided to use a [Twist](https://twistapp.com/) integration as the interface for our app. To do so, we created a oAuth2 integration with REST hooks as listeners.


### Implementation

The data flow starts in the Twist app. From there, we can send the image we want to extract text from. The image is received in our backend Flask server, where it is processed.

The image is sent through the MS Computer Vision API, which extracts words and their corresponding bounding boxes (in image coordinates). With this information we need to generate the plaintext file. To do so, we discretize the image coordinates in a grid, which will then be translated to a text file (each cell is a character). The tricky part here is to make a good choice for the cells width and height, since this will directly affect the separation between words. A low value leads to a high separation, since more lines fit in the same amount of space. On the contrary, a high value leads to a low separation, potentially generating collisions between words.

Once the grid has been filled up with the information returned from the API call, we generate the plaintext file. This file is then uploaded to Twist through an API call. Finally, another Twist API call sends the file url as an attachment to the same thread that initiated the interaction.
