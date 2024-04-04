### Pixlr API Usage Guide

This Python module provides a simple interface for automating actions on the Pixlr platform, including registration, email verification, generating images, and deleting accounts. Below is a guide on how to use this module effectively:

#### Prerequisites:

- Python 3.x installed on your system.
- Necessary Python libraries installed, including `requests`.

#### Usage Steps:

1.  **Import the Module:**

    ```python
    from pixlr_private_api.main import PixlrApi
    ```

2.  **Initialize PixlrApi Object:**

    ```python
    pixlr = PixlrApi()
    ```

3.  **Registration:**

    ```python
    registered = pixlr.register()
    if registered:
        print("Successfully registered!")
    ```

4.  **Email Verification:**

    ```python
    verified = pixlr.verify_email()
    if verified:
        print("Email verified successfully!")
    ```

5.  **Generate Image:**

    ```python
    # Provide width, height, amount, and prompt for image generation
    images = pixlr.generate_image(width, height, amount, prompt)
    # 'images' will contain paths to the generated images
    ```

6.  **Delete Account (Optional):**

    ```python
    deleted = pixlr.delete_account()
    if deleted:
        print("Account deleted successfully!")
    ```

7.  **Remove An Image Background**

    ```python

    image_path = "/tmp/1e62c8856e064e04b1cf3d71739a1d2b.png" # The image of your coice
    pixlr.remove_bg(image_path) # Returns a new image Path with the background Removed!
    ```

8.  **Auto Fix - Automatically does fixing**

    ```python

    image_path = "/tmp/1e62c8856e064e04b1cf3d71739a1d2b.png" # The image of your coice
    pixlr.auto_fix(image_path) # Returns a new image Path with auto fixes applied
    ```

9.  **LowLight Enhance - Enhances the Quality of Image if in Low-Light**

    ```python

    image_path = "/tmp/1e62c8856e064e04b1cf3d71739a1d2b.png" # The image of your coice
    pixlr.lowlight_enhance(image_path) # Returns a new image Path with Enhanced Low Light
    ```

10. **Super Resolution - Scales the Image Up BY an integer Value**

    ```python

    image_path = "/tmp/1e62c8856e064e04b1cf3d71739a1d2b.png" # The image of your coice
    scale = 2
    pixlr.super_resolution(image_path, scale=scale) # Returns a new image Path with Enhanced Low Light
    ```

11. **Style Transfer - Transfers the Style from one image to another!**

    ```python

    image_path = "/tmp/1e62c8856e064e04b1cf3d71739a1d2b.png" # The image of your coice
    image_style = "/tmp/some-style-image.png"
    pixlr.super_resolution(image_path, image_style) # Returns a new image Path with Transfered Style!
    ```

12. **Image Caption Generating - Generating Captions/Descriptions From Images**

    ```python

    image_path = "/tmp/1e62c8856e064e04b1cf3d71739a1d2b.png" # The image of your coice
    pixlr.generate_image_caption(image_path) # Returns a string value of the caption!
    ```

13. **Image Tags Generating - Generating Tags/Keywords From Images**

    ```python

    image_path = "/tmp/1e62c8856e064e04b1cf3d71739a1d2b.png" # The image of your coice
    pixlr.generate_image_tags(image_path) # Returns a List of tags/keywords List[str]
    ```

### Additional Notes:

- Ensure to handle errors and exceptions appropriately for robust usage.
- This module interacts with Pixlr through web requests, so network connectivity is required.
- API requests may be rate-limited or subject to changes by Pixlr, so handle responses accordingly.
- Phosus, The Second API integrated in to this, thanks to Pixlr giving us free api keys, does leave a fingerprint in the temp folder (Mask Images for removing backgrounds, But no worries, your Operating System does delete them on restart).

This guide provides a basic overview of how to use the Pixlr API module. For detailed information on method parameters and return values, refer to the module's source code or documentation.
