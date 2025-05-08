// 图片预览功能
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // 检查是否已存在预览元素
                    let preview = document.getElementById('image-preview');
                    if (!preview) {
                        // 创建预览元素
                        preview = document.createElement('div');
                        preview.id = 'image-preview';
                        preview.className = 'mt-2';
                        preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-height: 200px;" alt="预览图片">`;
                        imageInput.parentNode.appendChild(preview);
                    } else {
                        // 更新预览图片
                        const img = preview.querySelector('img');
                        img.src = e.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // 表单验证
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const description = form.querySelector('#description');
            const image = form.querySelector('#image');
            
            // 如果表单包含这两个字段，检查至少有一个有值
            if (description && image) {
                if (!description.value && (!image.files || image.files.length === 0 || !image.files[0].name)) {
                    event.preventDefault();
                    alert('请提供物品描述或上传图片（至少一项）');
                }
            }
        });
    });
});

// 确认删除
function confirmDelete(itemId) {
    if (confirm('确定要删除这个物品吗？')) {
        window.location.href = `/admin/delete/${itemId}`;
    }
}