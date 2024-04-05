from django.template import Library, loader
from ..forms import AppointmentForm
from ..models import Portfolio, Category
from django.contrib.staticfiles import finders
import os

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.ERROR)


register = Library()

# https://localcoder.org/django-inclusion-tag-with-configurable-template


@register.simple_tag(takes_context=True)
def hero(context):
    t = loader.get_template(f"herobizds/_hero_{context['hero_type']}.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def featured_services(context):
    t = loader.get_template("herobizds/_featured_services.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def about(context):
    t = loader.get_template("herobizds/_about.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def clients(context):
    t = loader.get_template("herobizds/_clients.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def cta(context):
    t = loader.get_template("herobizds/_cta.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def onfocus(context):
    t = loader.get_template("herobizds/_onfocus.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def features(context):
    t = loader.get_template("herobizds/_features.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def services(context):
    t = loader.get_template("herobizds/_services.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def testimonials(context):
    t = loader.get_template("herobizds/_testimonials.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def pricing(context):
    t = loader.get_template("herobizds/_pricing.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def faq(context):
    t = loader.get_template("herobizds/_faq.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def portfolio(context):
    t = loader.get_template("herobizds/_portfolio.html")
    context.update({
        'categories': Category.objects,
        'items': Portfolio.objects,
    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def team(context):
    t = loader.get_template("herobizds/_team.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def blog(context):
    t = loader.get_template("herobizds/_blog.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


@register.simple_tag(takes_context=True)
def contact(context):
    t = loader.get_template("herobizds/_contact.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())

@register.simple_tag(takes_context=True)
def breadcrumb(context):
    t = loader.get_template("herobizds/breadcrumb.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())