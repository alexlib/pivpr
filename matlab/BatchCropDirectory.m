
%--------------------------------------------------------------------------
% [] = BatchCropDirectory(path,border,format)
% function autocrops entire directory of image files and rewrites them
%       path:     filepath of directory containing images to crop
%       format:   any valid image files 'jpg','tif','png' etc.
%                 formats must be done one at a time.
%       border:   number of pixels of white space to leave on the perimeter
%
% WARNING! BatchCropOutput overwrites existing images
%--------------------------------------------------------------------------
function []=BatchCropDirectory(path,border,format) 
    cd(path);

    d=dir(strcat('*.',format))
    
for m=1:size(d)  
    
        file=d(m).name;
        Image=imread(file);
        size(Image)
        disp(strcat('Loaded Image........',d(m).name));
if Image(border,:,1:3)==255    
    
    % set the inital coordinates of corner points of crop window to [0 0]
    TL=[0 0];BL=[0 0];TR=[0 0];BR=[0 0];
        
    %find the top edge of the crop window
        i=1;
        while TL(1)==0
            if Image(i,:,1:3)>=253
                i=i+1;
            else
                TL(1)=i-border;
                TR(1)=i-border;
            end
        end
    %find the botom edge of the crop window
        i=size(Image,1);
        while BL(1)==0
            if Image(i,:,1:3)>=253
                i=i-1;
            else
                BL(1)=i+border;
                BR(1)=i+border;
            end
        end
    %find the left edge of the crop window
        j=1;
        while TL(2)==0
            if Image(:,j,1:3)>=253
                j=j+1;
            else
                TL(2)=j-border;
                BL(2)=j-border;
            end
        end
    %find the right edge of the crop window
        j=size(Image,2);
        while BR(2)==0
            if Image(:,j,1:3)>=253
                j=j-1;
            else
                TR(2)=j+border;
                BR(2)=j+border;
            end
        end     
        disp(strcat('Cropped Image........',d(m).name));
        
%define new image only from the crop window then save it
    NewImage=Image(TL(1):BL(1),TL(2):TR(2),1:3);
    cd(path);
    imwrite(NewImage,strcat(path,'\',file));
else
disp('Image appears to already be cropped! try lowering border setting!');    
end

end

end



