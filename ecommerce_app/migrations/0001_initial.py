# Generated by Django 3.0.6 on 2020-10-02 01:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion_categoria', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('imagen_logo', models.ImageField(upload_to='logo_empresa')),
                ('telefono', models.CharField(max_length=50)),
                ('correo', models.CharField(max_length=100)),
                ('fecha_registro', models.DateField(auto_now_add=True)),
                ('direccion', models.TextField()),
                ('latitude_empresa', models.FloatField(blank=True, default=0.0, null=True)),
                ('longitude_empresa', models.FloatField(blank=True, default=0.0, null=True)),
                ('descripcion', models.TextField(verbose_name='descripcion_empresa')),
            ],
        ),
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion_genero', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion_marca', models.CharField(max_length=50)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.Categoria')),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen_producto', models.ImageField(upload_to='imagen_producto')),
                ('nombre_producto', models.CharField(blank=True, max_length=200, null=True)),
                ('descripcion_producto', models.CharField(blank=True, max_length=500, null=True)),
                ('modelo', models.CharField(blank=True, max_length=500, null=True)),
                ('fecha_registro', models.DateField(auto_now_add=True, null=True)),
                ('precio', models.FloatField(blank=True, default=0, null=True)),
                ('porcentaje_descuento', models.IntegerField(blank=True, default=0, null=True)),
                ('esta_descuento', models.BooleanField(default=False)),
                ('nuevo_producto', models.BooleanField(default=False)),
                ('estado_producto', models.BooleanField(default=False)),
                ('proveedor', models.CharField(blank=True, max_length=500, null=True)),
                ('categoria_genero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.Genero')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.Marca')),
            ],
        ),
        migrations.CreateModel(
            name='Redes_sociales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_facebook', models.CharField(blank=True, max_length=100, null=True)),
                ('url_instagram', models.CharField(blank=True, max_length=100, null=True)),
                ('correo', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Telegram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=200)),
                ('groupid', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TipoInventario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_inventario', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion_tipo_producto', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='Lote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('existencia', models.CharField(max_length=50)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_identidad', models.CharField(max_length=20)),
                ('nombres', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('numero_telefono', models.CharField(max_length=50)),
                ('fecha_nacimiento', models.DateField()),
                ('fecha_registro', models.DateField(auto_now_add=True)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='avatar')),
                ('genero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.Genero')),
                ('usuario_cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.CharField(max_length=50)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.Producto')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
